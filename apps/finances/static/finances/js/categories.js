// finances/static/finances/js/categories.js

// declare constant variables for categories table
document.addEventListener("DOMContentLoaded", () => {
    const popup = document.getElementById("category-popup");
    const id_input = document.getElementById("category-id");
    const name_input = document.getElementById("category-name");
    const type_input = document.getElementById("category-type");
    // TODO: temporary remove until goals is finished
    //const goal_input = document.getElementById("category-goal");
    const form_title = document.getElementById("form-title");
    const form = document.getElementById('category-form');
    const saveButton = document.getElementById('save-button');
    const cancelButton = document.getElementById('cancel-button');
    cancelButton.addEventListener("click", () => popup.close());

    // initialize the button state for the "save" button
    // make it grayed out to start/when empty
    saveButton.disabled = !form.checkValidity();

    // turn save button highlighting on or off based on user's typing
    form.addEventListener('input', () => {
        saveButton.disabled = !form.checkValidity();
    });

    // create a new category with the following values
    document.getElementById("new-category-button").addEventListener("click", () => {
        id_input.value = "";
        name_input.value = "";
        type_input.value = "";
        // TODO: temporary remove until goals is finished
        // goal_input.value = "";
        form_title.textContent = "Add Category";
        popup.showModal();
    });

    document.querySelectorAll(".edit-button").forEach(button => {
        button.addEventListener("click", () => {
            const row = button.closest("tr");
            id_input.value = row.dataset.id;
            name_input.value = row.dataset.name;
            type_input.value = row.dataset.entry_type;

            // TODO: temporary remove until goals is finished
            //goal_input.value = row.dataset.goal;
            form_title.textContent = "Edit Category";
            popup.showModal();
        });
    });

    // delete the category
    document.querySelectorAll(".delete-button").forEach(button => {
        button.addEventListener("click", event => {
            if (!confirm("Are you sure you want to delete this category?")) {
                event.preventDefault();
            }
        });
    });

});