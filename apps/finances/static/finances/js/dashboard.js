async function get_totals() {
    const balance_form = document.getElementById("balance-form");
    const income_total = document.getElementById("income-total-display");
    const expense_total = document.getElementById("expense-total-display");
    const net_total = document.getElementById("net-total-display");

    const form = new FormData(balance_form);
    const params = new URLSearchParams();

    if (form.get("start_date_input") != "") params.append("start", form.get("start_date_input"));
    if (form.get("end_date_input") != "") params.append("end", form.get("end_date_input"));

    const res = await fetch(`/accounts/totals?${params}`);
    const totals = await res.json();

    const currency_formatter = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

    income_total.innerHTML = currency_formatter.format(totals.income);
    expense_total.innerHTML = currency_formatter.format(totals.expense);
    net_total.innerHTML = currency_formatter.format(totals.net);
}

get_totals();
