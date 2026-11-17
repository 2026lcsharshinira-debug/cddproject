
// Display confirmation before deleting a student
function confirmDelete() {
    return confirm("Are you sure you want to delete this student?");
}

// Automatically hide success and error messages
document.addEventListener("DOMContentLoaded", function () {

    const messages = document.querySelectorAll(".message");

    messages.forEach(function (message) {
        setTimeout(function () {
            message.style.transition = "opacity 0.5s";
            message.style.opacity = "0";

            setTimeout(function () {
                message.remove();
            }, 500);

        }, 4000);
    });

});
