// Get all of the table rows (the entries)
const entries = document.querySelectorAll(".entry");

// If editing isn't active, add an event listener to each entry to be able to select multiple at a time for deletion
// This also allows css to target each selected element to change its color
if(entries.length > 0 && !entries[0].classList.contains("editing-active")) {
    entries.forEach((entry) => {
        entry.addEventListener("click", function() {
            this.classList.toggle("selected");
        });
    });
}

// ============================================
// BUTTONS
// ============================================
const transactionsPageURL = document.querySelector("#transactions-url").dataset.url;
const deleteButton = document.querySelector("#trans-delete");
const editButton = document.querySelector("#trans-edit");
const resetButton = document.querySelector("#select-reset");

// Helper function to get selected entries
function getSelectedEntries() {
    return document.querySelectorAll(".entry.selected");
}

// delete selected entries
deleteButton.addEventListener("click", function() {
    const selectedEntries = getSelectedEntries();

    if (selectedEntries.length === 0) {
        alert("Select at least one transaction to delete.");
        return;
    }

    const confirmMsg = selectedEntries.length === 1
        ? "Delete this transaction?"
        : `Delete ${selectedEntries.length} transactions?`;

    if (confirm(confirmMsg)) {
        // Delete selected entries
        let deletePromises = [];
        selectedEntries.forEach((entry) => {
            const entryId = entry.id.replace("entry-", "");
            const deleteURL = `/finances/transactions/delete/${entryId}`;
            deletePromises.push(
                fetch(deleteURL, {
                    method: "GET",
                })
            );
        });

        // Wait for all deletions to complete, then reload
        Promise.all(deletePromises)
            .then(() => {
                window.location.href = transactionsPageURL;
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("Transactions could not be deleted. Please try again.");
            });
    }
});

// edit single selected entry, only if exactly one is selected
editButton.addEventListener("click", function() {
    const selectedEntries = getSelectedEntries();

    if (selectedEntries.length === 0) {
        alert("Click on a transaction to select it for editing.");
        return;
    }

    if (selectedEntries.length > 1) {
        alert("Select only one transaction to edit.");
        return;
    }

    // Get entry id and navigate to edit
    const entryId = selectedEntries[0].id.replace("entry-", "");
    window.location.href = `${transactionsPageURL}?edit=${entryId}`;
});


// Reset button - deselect all
if (resetButton) {
    resetButton.addEventListener("click", function() {
        const selectedEntries = getSelectedEntries();
        selectedEntries.forEach((entry) => {
            entry.classList.remove("selected");
        });
    });
}
