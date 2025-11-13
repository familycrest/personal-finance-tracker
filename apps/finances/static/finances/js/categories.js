document.addEventListener("DOMContentLoaded", () => {

    // Get containers and fields
    const popup = document.getElementById("category-popup");
    const form = document.getElementById("category-form")
    const id_input = document.getElementById("category-id");
    const name_input = document.getElementById("category-name");
    const type_input = document.getElementById("category-type");
    const type_field = type_input ? type_input.closest("p") : null;
    const form_title = document.getElementById("form-title");

    if (!popup || !form || !name_input) return;

    // Client-side check for duplicate category name
    form.addEventListener("submit", (event) => {
        
        // Clear server-side error message
        name_input.setCustomValidity("");

        const new_name = (name_input.value || "").trim().toLowerCase();
        const current_id = (id_input.value || "").toString();

        // Allow normal handling if there is no new name
        if (!new_name) {
            return;
        }

        let is_duplicate = false;

        document.querySelectorAll(".category-card").forEach(cat => {
            const cat_name = (cat.dataset.name || "").trim().toLowerCase();
            const cat_id = (cat.dataset.id || "").trim().toString();

            // If new name has the same name as another category, 
            // but different ID, it is a duplicate
            if (cat_name === new_name && cat_id !== current_id) {
                is_duplicate = true;
            }
        });

        if (is_duplicate) {
            // Stop form from submitting
            event.preventDefault();

            // Show error message
            name_input.setCustomValidity("You already have a category with this name.");
            name_input.reportValidity();
            name_input.focus();
        }

    })

    // Add Category — open blank form
    document.getElementById("new-category-button").addEventListener("click", () => {
        // Clear any previous error
        name_input.setCustomValidity("");

        // Reset the field values
        id_input.value = "";
        name_input.value = "";
        type_input.value = "";
        form_title.textContent = "Add Category";

        // Reset entry type field visibility
        type_field.style.display = "";

        popup.showModal();
    });

    // Edit Category — fill form from card data
    document.querySelectorAll(".edit-button").forEach(button => {
        button.addEventListener("click", () => {
            const card = button.closest(".category-card");
            if (!card) return;

            // Clear any previous error
            name_input.setCustomValidity("");

            // Set fields to correct values or blank if the values were invalid
            id_input.value = card.dataset.id || "";
            name_input.value = card.dataset.name || "";
            type_input.value = card.dataset.entry_type || "";
            form_title.textContent = "Edit Category";
            
            // Hide entry type field
            type_field.style.display = "none"

            popup.showModal();
        });
    });

    // Cancel Button — close popup
    document.getElementById("cancel-button").addEventListener("click", () => popup.close());

    // Delete Confirmation
    document.querySelectorAll(".delete-button").forEach(button => {
        button.addEventListener("click", event => {
            if (!confirm("Are you sure you want to delete this category?")) {
                event.preventDefault();
            }
        });
    });
});