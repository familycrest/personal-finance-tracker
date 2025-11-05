// Get the goals page and the goals delete page urls from the template to be able to use the django url tag
const goalsPageURL = document.querySelector("#goals-url").dataset.url;
const deleteGoalsViewURL = document.querySelector("#delete-goals-url").dataset.url;

// ============================================
// SHARED UTILITIES
// ============================================
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

    return null;
}

function getSelectedGoals(className) {
    return document.querySelectorAll(`.${className}.selected`);
}

// Send account goal ids and category goal ids to the goal deletion view.
function sendGoalIds(goals, goalType) {
    let goalIdsToRm = [];

    // Get ids from the goals to send to the django view
    goals.forEach(element => {
        let id = element.getAttribute("goal-id");
        goalIdsToRm.push(id);
    });
    let body = "";
    if(goalType === "account") {
        body = JSON.stringify({acctGoals: goalIdsToRm});
    }
    else if(goalType === "category") {
        body = JSON.stringify({catGoals: goalIdsToRm});
    }
    // Send the id list to the goal deletion view then deal with the response
    fetch(deleteGoalsViewURL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: body,
    }).then(response => {
        if(!response.ok) {
            throw new Error("Server response was not ok");
        }
        else {
            window.location.href = goalsPageURL;
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Goals were not able to be deleted. Please try again.");
    });
}


// ============================================
// SHARED DIALOGS
// ============================================
// Message Dialog
let msg_dialog = document.querySelector("#msg-dialog");
let msg = document.querySelector("#msg");
let msg_close_btn = document.querySelector("#msg-close");
msg_close_btn.addEventListener('click', function() {
    msg_dialog.close();
});

// Goal delete dialog
const goal_delete_dialog = document.querySelector("#goal-delete-dialog");
const delete_cancel_btn = document.querySelector("#goal-delete-cancel");
const delete_confirm_btn = document.querySelector("#goal-delete-confirm");

// Store what to delete when delete confirm is clicked
let pendingDeletion = null;

// Button for closing the deletion dialog, also clears the list of elements to delete
delete_cancel_btn.addEventListener('click', function() {
    goal_delete_dialog.close();
    pendingDeletion = null;
});

// Button for confirming deletion, only does anything if there are actually things to delete
delete_confirm_btn.addEventListener('click', function() {
    if(pendingDeletion) {
        sendGoalIds(pendingDeletion.goals, pendingDeletion.type);
        pendingDeletion = null;
    }
});


// ============================================
// ACCOUNT GOALS
// ============================================
// Account goals table buttons
const acct_goal_add_btn = document.querySelector("#acct-goal-add-btn");
const acct_goal_edit_btn = document.querySelector("#acct-goal-edit-btn");
const acct_open_delete_btn = document.querySelector("#acct-goal-delete-btn"); // Opens delete dialog

// AccountGoal add dialog
const acct_goal_add_dialog = document.querySelector("#acct-goal-add-dialog");
const acct_goal_add_cancel_btn = document.querySelector("#acct-goal-add-cancel");
acct_goal_add_btn.addEventListener('click', function() {
    acct_goal_add_dialog.showModal();
});
acct_goal_add_cancel_btn.addEventListener('click', function() {
    acct_goal_add_dialog.close();
});
// Show account goal add dialog if an error is present in the form, set by view
if (acct_goal_add_dialog.dataset.showOnLoad === "true") {
    acct_goal_add_dialog.showModal();
}

// AccountGoal edit dialog
const acct_goal_edit_dialog = document.querySelector("#acct-goal-edit-dialog");
const acct_goal_edit_cancel_btn = document.querySelector("#acct-goal-edit-cancel");

acct_goal_edit_btn.addEventListener('click', function() {
    let selected_acct_goals = getSelectedGoals("acct-goal-row");
    
    if(selected_acct_goals.length == 0) {
        msg.textContent = "Click on an account goal to select it for editing.";
        msg_dialog.showModal();
    }
    else if(selected_acct_goals.length > 1) {
        msg.textContent = "Select only one account goal to edit.";
        msg_dialog.showModal();
    }
    else {
        // Get goal id and use it as a url parameter to send to the view for editing
        let goal_id = selected_acct_goals[0].getAttribute("goal-id");
        window.location.href = `${goalsPageURL}?goal-id=${goal_id}&form_type=edit-acct-goal`;
    }
});

acct_goal_edit_cancel_btn.addEventListener('click', function() {
    acct_goal_edit_dialog.close();
});

// Show account goal edit dialog if an error is present in the form, set by view
if(acct_goal_edit_dialog.dataset.showOnLoad === "true") {
    acct_goal_edit_dialog.showModal();
}

// AccountGoal delete dialog setup
acct_open_delete_btn.addEventListener('click', function() {
    let selectedAcctGoals = getSelectedGoals("acct-goal-row");
    if(selectedAcctGoals.length == 0) {
        msg.textContent = "Select at least one account goal to delete.";
        msg_dialog.showModal();
    }
    else {
        // Store selected account goals to delete
        pendingDeletion = {
            goals: selectedAcctGoals,
            type: "account"
        };
        goal_delete_dialog.showModal();
    }
    
});


// ============================================
// CATEGORY GOALS  
// ============================================
// Category goals table buttons
const cat_goal_add_btn = document.querySelector("#category-goals-add");
const cat_goal_edit_btn = document.querySelector("#category-goals-edit");
const cat_open_delete_btn = document.querySelector("#category-goals-delete");

// Category goals filter
const category_filter = document.querySelector("#category-filter");

// Function to show only the selected category's goals (or all category goals)
function filterCatGoals() {
    const selected_category = category_filter.value;
    const rows = document.querySelectorAll(".cat-goal-row");
    // Row that shows when there are no category goals to show
    const no_cat_goals_row = document.querySelector("#no-cat-goals-row");
    // Hide row again if it was shown by the previous selection
    no_cat_goals_row.style.display = "none";

    let rows_shown = 0;
    rows.forEach(row => {
        // If selected category is empty ("All Categories" value is "") or the category is correct show the goal's row
        if (!selected_category || row.dataset.categoryId === selected_category) {
            row.style.display = "";  // Show
            ++rows_shown;
        } else {
            row.style.display = "none";  // Hide
        }
    });
    if(rows_shown === 0) {
        no_cat_goals_row.style.display = "";
    }
}
// Run the filter to make sure all the initially shown rows are correct then add an event listener to the select element
filterCatGoals();
category_filter.addEventListener('change', filterCatGoals);

// Category goal add dialog
let cat_goal_add_dialog = document.querySelector("#cat-goal-add-dialog");
const cat_goal_add_cancel_btn = document.querySelector("#cat-goal-add-cancel");

cat_goal_add_btn.addEventListener('click', function() {
    cat_goal_add_dialog.showModal();
});

cat_goal_add_cancel_btn.addEventListener('click', function() {
    cat_goal_add_dialog.close();
});

if(cat_goal_add_dialog.dataset.showOnLoad === "true") {
    cat_goal_add_dialog.showModal();
}

// CategoryGoal edit dialog
const cat_goal_edit_dialog = document.querySelector("#cat-goal-edit-dialog");
const cat_goal_edit_cancel_btn = document.querySelector("#cat-goal-edit-cancel");

cat_goal_edit_btn.addEventListener('click', function() {
    let selected_cat_goals = getSelectedGoals("cat-goal-row");

    if(selected_cat_goals.length == 0) {
        msg.textContent = "Click on a category goal to select it for editing.";
        msg_dialog.showModal();
    }
    else if(selected_cat_goals.length > 1) {
        msg.textContent = "Select only one category goal to edit.";
        msg_dialog.showModal();
    }
    else {
        let goal_id = selected_cat_goals[0].getAttribute("goal-id");
        window.location.href = `${goalsPageURL}?goal-id=${goal_id}&form_type=edit-cat-goal`;
    }
});

cat_goal_edit_cancel_btn.addEventListener('click', function() {
    cat_goal_edit_dialog.close();
});

if(cat_goal_edit_dialog.dataset.showOnLoad === "true") {
    cat_goal_edit_dialog.showModal();
}

// CategoryGoal delete
cat_open_delete_btn.addEventListener('click', function() {
    let selectedCatGoals = getSelectedGoals("cat-goal-row");
    if(selectedCatGoals.length == 0) {
        msg.textContent = "Select at least one category goal to delete.";
        msg_dialog.showModal();
    }
    else {
        pendingDeletion = {
            goals: selectedCatGoals,
            type: "category"
        };
        goal_delete_dialog.showModal();
    }
});


// ============================================
// OTHER
// ============================================
// Add an event listener to each row that represents a goal to select it when clicked
const rows = document.querySelectorAll("tr[goal-id]");

rows.forEach(row => {
    row.addEventListener('click', function() {
        this.classList.toggle('selected');
    });
});