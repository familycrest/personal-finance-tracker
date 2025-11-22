const acct_chart = document.getElementById("acct-chart");
const acct_chart_info = document.getElementById("acct-chart-info").dataset;
const cat_chart = document.getElementById("cat-chart");
const cat_chart_info = document.getElementById("cat-chart-info").dataset;
const expense_pie = document.getElementById("expense-pie");
const expense_pie_div = document.getElementById("expense-pie-div");
const income_pie = document.getElementById("income-pie");
const income_pie_div = document.getElementById("income-pie-div");
const savings_chart = document.getElementById("savings-chart");

let acct_data = JSON.parse(document.getElementById('acct-data').textContent);
let cat_data = JSON.parse(document.getElementById('cat-data').textContent);
let exp_pie_data = JSON.parse(document.getElementById('exp-pie-data').textContent);
let inc_pie_data = JSON.parse(document.getElementById('inc-pie-data').textContent);
let savings_data = JSON.parse(document.getElementById('savings-data').textContent);

// Make the subtitles for the acct chart and cat chart
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
      },
      legend: {
        onClick: null  // Disable legend interaction
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
      },
      legend: {
        onClick: null  // Disable legend interaction
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});

// Function to process pie data; limits to 10 + another category aggregating the remainder,
// add percentages, and sort
function processPieData(pie_data) {
  // Convert to array format: [label, value]
  let data = Object.values(pie_data).map(arr => [arr[0], arr[1]]);

  // Sort by value (descending for legend)
  data.sort((a, b) => b[1] - a[1]);

  // Calculate total of all transactions in the pie chart for calculating %s of total
  const total = data.reduce((sum, item) => sum + item[1], 0);

  // Limit to top 10 items, aggregate rest into "Other" category
  if (data.length > 10) {
    const top_ten = data.slice(0, 10);
    const remaining = data.slice(10);
    const aggregate_sum = remaining.reduce((sum, item) => sum + item[1], 0);
    data = [...top_ten, ['Other', aggregate_sum]];
  }

  // Create graph labels
  const labels = data.map(item => item[0]);
  const values = data.map(item => item[1]);

  // Calculate category percentages of total transactions for tooltips
  const percentages = data.map(item => {
    return total > 0 ? ((item[1] / total) * 100).toFixed(2) : 0;
  });

  return { labels: labels, values: values, percentages: percentages };
}

// Process expense and income pie data
exp_pie_data = processPieData(exp_pie_data);
inc_pie_data = processPieData(inc_pie_data);

// Pie chart for showing expenses for each category in the chosen time period
// Only show the pie chart if it has data, else show a message for no data
if(exp_pie_data.labels.length > 0) {
  expense_pie_div.removeAttribute("hidden");
  const exp_chart = new Chart(expense_pie, {
    type: 'pie',
    data: {
      labels: exp_pie_data.labels,
      datasets: [{
        data: exp_pie_data.values
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 1,
      plugins: {
        title: {
          display: true,
          position: 'top',
          text: "Expenses By Category",
          font: {
            size: 18,
          },
        },
        legend: {
          maxWidth: 200,
          position: 'right',
          onClick: null  // Disable legend interaction
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.label || '';
              const value = context.parsed;
              const percentage = exp_pie_data.percentages[context.dataIndex];
              return `${label}: ${value} (${percentage}%)`;
            }
          }
        }
      }
    }
  });
}
else {
  let exp_pie_no_data_msg = document.getElementById("exp-pie-no-data-msg");
  exp_pie_no_data_msg.removeAttribute("hidden");
}


// Pie chart for showing income for each category in the chosen time period
// Only show the pie chart if it has data, else show a message for no data
if(inc_pie_data.labels.length > 0) {
  income_pie_div.removeAttribute("hidden");
  const inc_chart = new Chart(income_pie, {
    type: 'pie',
    data: {
      labels: inc_pie_data.labels,
      datasets: [{
        data: inc_pie_data.values
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 1,
      plugins: {
        title: {
          display: true,
          position: 'top',
          text: "Income By Category",
          font: {
            size: 18,
          },
        },
        legend: {
          maxWidth: 200,
          position: 'right',
          onClick: null  // Disable legend interaction
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.label || '';
              const value = context.parsed;
              const percentage = inc_pie_data.percentages[context.dataIndex];
              return `${label}: ${value} (${percentage}%)`;
            }
          }
        }
      }
    }
  });
}
else {
  let inc_pie_no_data_msg = document.getElementById("inc-pie-no-data-msg");
  inc_pie_no_data_msg.removeAttribute("hidden");
}


new Chart(savings_chart, {
  type: 'line',
  data: {
    labels: Object.values(savings_data).map(item => item[0]),
    datasets: [{
      data: Object.values(savings_data).map(item => item[1]),
    }],
  },
  options: {
    plugins: {
      legend: {
        display: false
      }
    }
  }
});
