
# Use Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Store database in Docker volume
ENV DATA_DIR=/data

RUN mkdir -p /data

# Expose Flask port
EXPOSE 5000

# Start Flask application
CMD ["python", "app.py"]
