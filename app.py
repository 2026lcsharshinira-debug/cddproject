
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "hostelroomallocation_secret"

DATABASE = "hostel.db"


# Database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database and tables
def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            usn TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            year TEXT NOT NULL,
            room_id INTEGER,
            FOREIGN KEY(room_id) REFERENCES rooms(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT UNIQUE NOT NULL,
            capacity INTEGER NOT NULL
        )
    """)

    # Insert sample rooms only if the table is empty
    count = conn.execute(
        "SELECT COUNT(*) FROM rooms"
    ).fetchone()[0]

    if count == 0:
        rooms = [
            ("101", 3),
            ("102", 3),
            ("103", 3),
            ("104", 3),
            ("105", 3),
            ("106", 3)
        ]

        conn.executemany("""
            INSERT INTO rooms (room_number, capacity)
            VALUES (?, ?)
        """, rooms)

    conn.commit()
    conn.close()


# Dashboard
@app.route("/")
def index():
    conn = get_db()

    students = conn.execute("""
        SELECT students.*, rooms.room_number
        FROM students
        LEFT JOIN rooms ON students.room_id = rooms.id
        ORDER BY students.id DESC
    """).fetchall()

    rooms = conn.execute("""
        SELECT rooms.*,
        COUNT(students.id) AS occupied
        FROM rooms
        LEFT JOIN students ON rooms.id = students.room_id
        GROUP BY rooms.id
    """).fetchall()

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    allocated = conn.execute(
        "SELECT COUNT(*) FROM students WHERE room_id IS NOT NULL"
    ).fetchone()[0]

    available = sum(
        room["capacity"] - room["occupied"]
        for room in rooms
    )

    conn.close()

    return render_template(
        "index.html",
        students=students,
        rooms=rooms,
        total_students=total_students,
        allocated=allocated,
        available=available
    )


# Add student
@app.route("/add_student", methods=["POST"])
def add_student():
    name = request.form["name"].strip()
    usn = request.form["usn"].strip()
    department = request.form["department"].strip()
    year = request.form["year"]

    if not all([name, usn, department, year]):
        flash("Please fill all student details.", "error")
        return redirect(url_for("index"))

    conn = get_db()

    try:
        conn.execute("""
            INSERT INTO students
            (name, usn, department, year)
            VALUES (?, ?, ?, ?)
        """, (name, usn, department, year))

        conn.commit()
        flash("Student added successfully!", "success")

    except sqlite3.IntegrityError:
        flash("USN already exists. Enter a unique USN.", "error")

    finally:
        conn.close()

    return redirect(url_for("index"))


# Automatically allocate room
@app.route("/allocate/<int:student_id>", methods=["POST"])
def allocate(student_id):
    conn = get_db()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    if student is None:
        flash("Student not found.", "error")
    elif student["room_id"] is not None:
        flash("Student already has a room.", "error")
    else:
        room = conn.execute("""
            SELECT rooms.id, rooms.room_number
            FROM rooms
            LEFT JOIN students ON rooms.id = students.room_id
            GROUP BY rooms.id
            HAVING COUNT(students.id) < rooms.capacity
            ORDER BY rooms.room_number
            LIMIT 1
        """).fetchone()

        if room:
            conn.execute("""
                UPDATE students
                SET room_id = ?
                WHERE id = ?
            """, (room["id"], student_id))

            conn.commit()
            flash(
                f"Room {room['room_number']} allocated successfully!",
                "success"
            )
        else:
            flash("Sorry! No rooms are available.", "error")

    conn.close()
    return redirect(url_for("index"))


# Vacate room
@app.route("/vacate/<int:student_id>", methods=["POST"])
def vacate(student_id):
    conn = get_db()

    conn.execute("""
        UPDATE students
        SET room_id = NULL
        WHERE id = ?
    """, (student_id,))

    conn.commit()
    conn.close()

    flash("Room vacated successfully!", "success")
    return redirect(url_for("index"))


# Delete student
@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = get_db()

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    conn.commit()
    conn.close()

    flash("Student deleted successfully!", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
