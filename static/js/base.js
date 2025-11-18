const notif_button = document.getElementById("notification-toggle");
const unread_count_display = document.getElementById("unread-count");
const total_count_display = document.getElementById("total-count");

async function notif_mark_read (id) {
    const res = await fetch(`/accounts/notifications/${id}/mark_read`);

    const el = document.getElementById(`notification-card-${id}`);
    el.classList.remove("notification-unread");
    el.classList.add("notification-read");

    const btn = document.getElementById(`notification-read-${id}`);
    btn.remove();
    
    refresh_notifs();
}

async function notif_delete (id) {
    const res = await fetch(`/accounts/notifications/${id}/delete`);

    const el = document.getElementById(`notification-card-${id}`);
    el.remove();
    
    refresh_notifs();
}

function refresh_notifs () {
    const unread = document.getElementsByClassName("notification-unread");
    const read = document.getElementsByClassName("notification-read");
    const notif_list = document.getElementById("notification-list")
    const notif_button = document.getElementById("notification-toggle");

    notif_list.replaceChildren(...unread, ...read);

    unread_count_display.innerHTML = `${unread.length} unread`;
    total_count_display.innerHTML = `${unread.length + read.length} total`;
    
    if (unread.length == 0) {
        notif_button.classList.remove("btn-bg-important");
        notif_button.classList.add("btn-bg-secondary");
    }
}