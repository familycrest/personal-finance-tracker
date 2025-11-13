const acct_chart = document.getElementById("acct-chart");
const acct_chart_info = document.getElementById("acct-chart-info").dataset;
const cat_chart = document.getElementById("cat-chart");
const cat_chart_info = document.getElementById("cat-chart-info").dataset;
console.log(acct_chart_info.dataset);

let acct_data = JSON.parse(document.getElementById('acct-data').textContent);
let cat_data = JSON.parse(document.getElementById('cat-data').textContent);

let acct_chart_title = `All transaction data from ${acct_chart_info.startDate} to ${acct_chart_info.endDate }`;
let cat_category = cat_chart_info.catCategory;
let cat_chart_title;
if(cat_category != "None") {
  cat_chart_title = `Transaction data for ${cat_chart_info.catCategory} from ${cat_chart_info.startDate} to ${cat_chart_info.endDate}`;
}
else {
  cat_chart_title = "No category selected for data to be shown";
}


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
        position: "bottom"
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});

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
