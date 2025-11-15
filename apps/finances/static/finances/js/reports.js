const acct_chart = document.getElementById("acct-chart");
const acct_chart_info = document.getElementById("acct-chart-info").dataset;
const cat_chart = document.getElementById("cat-chart");
const cat_chart_info = document.getElementById("cat-chart-info").dataset;
const expense_pie = document.getElementById("expense-pie");
const income_pie = document.getElementById("income-pie");

let acct_data = JSON.parse(document.getElementById('acct-data').textContent);
let cat_data = JSON.parse(document.getElementById('cat-data').textContent);
let exp_pie_data = JSON.parse(document.getElementById('exp-pie-data').textContent);
let inc_pie_data = JSON.parse(document.getElementById('inc-pie-data').textContent);


let acct_chart_title = `All transaction data from ${acct_chart_info.startDate} to ${acct_chart_info.endDate }`;
let cat_category = cat_chart_info.catCategory;
let cat_chart_title;
if(cat_category != "None") {
  cat_chart_title = `Transaction data for ${cat_chart_info.catCategory} from ${cat_chart_info.startDate} to ${cat_chart_info.endDate}`;
}
else {
  cat_chart_title = "Category transaction chart. Pick a category";
}

// Chart for account wide data for different time periods and data intervals
// (Interval = Data point size = A sum for all transactions in a day, week, or month)
new Chart(acct_chart, {
  type: 'bar',
  data: {
    labels: Object.keys(acct_data),
    datasets: [{
      label: "Expenses",
      data: Object.values(acct_data).map(item => item.EXPENSE),
      borderWidth: 1
    },
    {
      label: "Incomes",
      data: Object.values(acct_data).map(item => item.INCOME),
      borderWidth: 1
    }
  ]
  },
  options: {
    plugins: {
      title: {
        display: true,
        text: acct_chart_title,
        position: "bottom",
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});

// Chart for specific data for different time periods and data intervals
// (Interval = Data point size = A sum for all transactions in a day, week, or month)
new Chart(cat_chart, {
  type: 'bar',
  data: {
    labels: Object.keys(cat_data),
    datasets: [{
      label: "Expenses",
      data: Object.values(cat_data).map(item => item.EXPENSE),
      borderWidth: 1
    },
    {
      label: "Incomes",
      data: Object.values(cat_data).map(item => item.INCOME),
      borderWidth: 1
    }
  ]
  },
  options: {
    plugins: {
      title: {
        display: true,
        text: cat_chart_title,
        position: "bottom",
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});

// Pie chart for showing expenses for each category in the chosen time period
new Chart(expense_pie, {
  type: 'pie',
  data: {
    labels: Object.values(exp_pie_data).map(arr => arr[0]),
    datasets: [{
      data: Object.values(exp_pie_data).map(arr => arr[1])
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
  }
});

// Pie chart for showing income for each category in the chosen time period
new Chart(income_pie, {
  type: 'pie',
  data: {
    labels: Object.values(inc_pie_data).map(arr => arr[0]),
    datasets: [{
      data: Object.values(inc_pie_data).map(arr => arr[1])
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
  }
});
