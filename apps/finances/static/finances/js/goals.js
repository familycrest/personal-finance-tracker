// Define a function to get a browser cookie of name name
function getCookie(name) {
    let cookieArr = document.cookie.split(";");

    for(let i = 0; i < cookieArr.length; i++) {
        let cookiePair = cookieArr[i].split("=");

        if(name == cookiePair[0].trim()) {
            // Cookie values are stored in uri format, so values like ' '
            // are made '%20'. This converts those values back.
            return decodeURIComponent(cookiePair[1])
        }
    }

    return null
}

// Send account goal ids and category goal ids to the goal deletion view.
function sendGoalIds() {
    let selectedAcctGoals = document.querySelectorAll(".acct_goal.selected");
    let selectedCatGoals = document.querySelectorAll(".cat_goal.selected");
    let aGoalIdsToRm = [];
    let cGoalIdsToRm = [];

    // Add account goals to list of account goals to remove
    selectedAcctGoals.forEach(element => {
        let id = element.getAttribute("goal_id");
        aGoalIdsToRm.push(id);
    });

    // Add category goals to list of category goals to remove
    selectedCatGoals.forEach(element => {
        let id = element.getAttribute("goal_id");
        cGoalIdsToRm.push(id);
    });

    // Send both lists to the goal deletion view then deal with the response
    fetch('/finances/goals/delete/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({acctGoals: aGoalIdsToRm, catGoals: cGoalIdsToRm}),
    }).then(response => {
        if(!response.ok) {
            throw new Error("Server response was not ok");
        }
        else {
            location.reload()
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Goals were not able to be deleted. Please try again.")
    });
}

// Add an event listener to each row that represents a goal to select it when clicked
const rows = document.querySelectorAll("tr[goal_id]");

rows.forEach(row => {
    row.addEventListener('click', function() {
        this.classList.toggle('selected');
    });
});

// Make constants for all buttons and dialogs
const add_btn = document.querySelector("#account_goals_add");
const edit_btn = document.querySelector("#account_goals_delete");
const open_delete_btn = document.querySelector("#account_goals_delete"); // Opens delete dialog
const delete_cancel_btn = document.querySelector("#delete_cancel");
const delete_confirm_btn = document.querySelector("#delete_confirm");

const delete_dialog = document.querySelector("#deletion_dialog");

// Open delete dialog
open_delete_btn.addEventListener('click', function() {
    delete_dialog.showModal();
});

// Close delete dialog without deleting objects
delete_cancel_btn.addEventListener('click', function() {
    delete_dialog.close();
});

// Delete selected goals
delete_confirm_btn.addEventListener('click', sendGoalIds);

