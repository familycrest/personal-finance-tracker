document.addEventListener("DOMContentLoaded", function () {
  // assign values to start at 0 and declare start and end date variables
  let totalIncome = 0,
    totalExpense = 0;
  // list of random "hilarious" quotes
  const quotes = [
    "When does it rain money? When there's change in the air",
    "My wallet is like an onion, opening it makes me cry.",
    "Girls just wanna have funds.",
    "My friends say I'm cheap, but I'm not buying it.",
    "What did the duck say after going shopping? Put it on my bill.",
    "If money doesn't grow on trees, then why do banks have branches?",
    "What do you call a belt made of $100? A waist of money.",
    "Why is money called dough? Because we need it.",
    "Knock, knock. Who's there? I.O... I.O who? Me, when can pay me back?",
    "Where do polar bears keep their money? At a snow bank.",
    "What do you call pasta with no money? Penne-less.",
    "Knock, knock. Who's there? Cash... Cash who? No, thanks, I prefer peanuts",
    "Why are money jokes funny? Because they make cents!",
    "Pigeons are the richest birds. They don't mind making deposits on expensive cars.",
    "I wish my wallet came with free refills!",
    "Why did the robber take a bath before he robbed the bank? To make a clean getaway.",
    "They call me lack toast intolerant the way I can't live without cash.",
  ];

  // display random quote js
  const quoteBox = document.getElementById("quote-line");
  if (quoteBox) {
    quoteBox.textContent = quotes[Math.floor(Math.random() * quotes.length)];
  }

  // clear button js
  const periodFilterResetButton = document.querySelector(
    "#period-filter-reset-button"
  );
  if (periodFilterResetButton) {
    periodFilterResetButton.addEventListener("click", function () {
      // this clear the dates and money totals in filter without needed to refresh
      document.getElementById("start_date_input").value = "";
      document.getElementById("end_date_input").value = "";

      // the clear button now also clears income, expense, and net total WITHOUT refreshing!
      const incomeTotal = document.getElementById("income-total-display");
      const expenseTotal = document.getElementById("expense-total-display");
      const netTotal = document.getElementById("net-total-display");

      if (incomeTotal) incomeTotal.textContent = "0";
      if (expenseTotal) expenseTotal.textContent = "0";
      if (netTotal) netTotal.textContent = "0";

      // reset totals back to 0 when hitting clear
      totalIncome = 0;
      totalExpense = 0;
    });
  }

  // calculate button js so it doesn't refresh when adding up totals
  const calculateButton = document.getElementById("calculate-button");
  if (calculateButton) {
    calculateButton.onclick = function () {
      // reset the totals back to prevent adding old amounts
      totalIncome = 0;
      totalExpense = 0;

      const startDateInput = document.getElementById("start_date_input").value;
      const endDateInput = document.getElementById("end_date_input").value;

      // convert input dates(strings) to objects
      function fixInputDate(inputValue) {
        // first check if input was given, returns null if so
        if (!inputValue) return null;

        // the input type is date in the format yyyy-mm-dd, temporarily remove the dashes and makes it a list of strings
        const parts = inputValue.split("-");

        const newDate = new Date(parts[0], parts[1] - 1, parts[2]);
        // make sure the date starts at midnight
        newDate.setHours(0, 0, 0, 0); // make sure comparison ignores time

        // return the new date in proper format to be compared
        return newDate;
      }

      // insert dates into the parseInputDate function
      const startDate = fixInputDate(startDateInput);
      const endDate = fixInputDate(endDateInput);

      // iterate through the table rows to gather data
      document
        .querySelectorAll(".transactions-table tbody tr")
        .forEach((row) => {
          // the dates in the transactions are gathered as strings initially from transactions table
          const transactionDateString = row.children[0].textContent.trim();

          // convert transaction date to an object so it can be properly compared by other variable
          // cannot compare strings to objects!
          const transactionDate = new Date(transactionDateString); // match formatting for year, month[Index], and day
          transactionDate.setHours(0, 0, 0, 0); // set time to midnight

          // < & > include the start and end dates
          if (startDate && transactionDate < startDate) return;
          if (endDate && transactionDate > endDate) return;

          // strip the $ and , for calculations
          const transactionAmount = parseFloat(
            row.children[2].textContent.replace(/[$,]/g, "")
          );
          const transactionType = row.children[3].textContent.trim();

          // skips the amount if it's empty
          if (isNaN(transactionAmount)) return;

          // sum up income/expense totals
          transactionType === "Income"
            ? (totalIncome += transactionAmount)
            : (totalExpense += transactionAmount);
        });

      // update totals without refreshing to the hundredth decimal place
      document.getElementById("income-total-display").textContent =
        totalIncome.toFixed(2);
      document.getElementById("expense-total-display").textContent =
        totalExpense.toFixed(2);
      document.getElementById("net-total-display").textContent = (
        totalIncome - totalExpense
      ).toFixed(2);
    };
  }
});
