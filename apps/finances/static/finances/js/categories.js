document.addEventListener("DOMContentLoaded", () => {
    const popup = document.getElementById("category-popup");
    const id_input = document.getElementById("category-id");
    const name_input = document.getElementById("category-name");
    const type_input = document.getElementById("category-type");
    const goal_input = document.getElementById("category-goal");
    const form_title = document.getElementById("form-title");

    document.getElementById("new-category-button").addEventListener("click", () => {
        id_input.value = "";
        name_input.value = "";
        type_input.value = "";
        goal_input.value = "";
        form_title.textContent = "Add Category";
        popup.showModal();
    });

    document.querySelectorAll(".edit-button").forEach(button => {
        button.addEventListener("click", () => {
            const row = button.closest("tr");
            id_input.value = row.dataset.id;
            name_input.value = row.dataset.name;
            type_input.value = row.dataset.entry_type;
            goal_input.value = row.dataset.goal;
            form_title.textContent = "Edit Category";
            popup.showModal();
        });
    });

    document.getElementById("cancel-button").addEventListener("click", () => popup.close());

    document.querySelectorAll(".delete-button").forEach(button => {
        button.addEventListener("click", event => {
            if (!confirm("Are you sure you want to delete this category?")) {
                event.preventDefault();
            }
        });
    });

});
