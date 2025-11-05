// document.addEventListener("DOMContentLoaded", () => {
//     // Category form IDs
//     const popup = document.getElementById("category-popup");
//     const id_input = document.getElementById("category-id");
//     const name_input = document.getElementById("category-name");
//     const type_input = document.getElementById("category-type");
//     const goal_input = document.getElementById("category-goal");
//     const form_title = document.getElementById("form-title");

//     // When user clicks add button, inputs default values to form elements and displays the popup
//     document.getElementById("new-category-button").addEventListener("click", () => {
//         id_input.value = "";
//         name_input.value = "";
//         type_input.value = "";
//         goal_input.value = "";
//         form_title.textContent = "Add Category";
//         popup.showModal();
//     });

//     // When user clicks edit button, inputs existing values to form elements and displays the popup
//     document.querySelectorAll(".edit-button").forEach(button => {
//         button.addEventListener("click", () => {
//             const row = button.closest("tr");
//             id_input.value = row.dataset.id;
//             name_input.value = row.dataset.name;
//             type_input.value = row.dataset.entry_type;
//             goal_input.value = row.dataset.goal;
//             form_title.textContent = "Edit Category";
//             popup.showModal();
//         });
//     });

//     // When user clicks cancel button, closes the popup without saving
//     document.getElementById("cancel-button").addEventListener("click", () => popup.close());

//     // When user clicks delete button, prompts for confirmation before proceeding
//     document.querySelectorAll(".delete-button").forEach(button => {
//         button.addEventListener("click", event => {
//             if (!confirm("Are you sure you want to delete this category?")) {
//                 event.preventDefault();
//             }
//         });
//     });

// });


document.addEventListener("DOMContentLoaded", () => {
    const popup = document.getElementById("category-popup");
    const id_input = document.getElementById("category-id");
    const name_input = document.getElementById("category-name");
    const type_input = document.getElementById("category-type");
    const form_title = document.getElementById("form-title");

    // Add Category — open blank form
    document.getElementById("new-category-button").addEventListener("click", () => {
        id_input.value = "";
        name_input.value = "";
        type_input.value = "";
        form_title.textContent = "Add Category";
        popup.showModal();
    });

    // Edit Category — fill form from card data
    document.querySelectorAll(".edit-button").forEach(button => {
        button.addEventListener("click", () => {
            const card = button.closest(".category-card");
            if (!card) return;

            id_input.value = card.dataset.id;
            name_input.value = card.dataset.name;
            type_input.value = card.dataset.entry_type;

            form_title.textContent = "Edit Category";
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