// Get all of the table rows (the entries)
const entries = document.querySelectorAll(".entry");

// If editing isn't active, add an event listener to each entry to be able to select multiple at a time for deletion
// This also allows css to target each selected element to change its color
if(!entries[0].classList.contains("editing-active")) {
    entries.forEach((entry) => {
        entry.addEventListener("click", function() {
            this.classList.toggle("selected");
        });
    });
}
