document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    
    form.addEventListener('submit', function(event) {
        event.preventDefault();  // Prevent the default form submission

        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        console.log(data)

        fetch('/api/view-reports', {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            let range = data.range;
            displayReports(data, range);
            drawCharts(data, range); 
        })
        .catch(error => {
            console.error('Error fetching the reports:', error);
            alert('Failed to fetch reports. Please try again.');
        });
    });
});

function displayReports(reports, range) {
    const reportsContainer = document.getElementById('reports-container');

    // Clear existing content
    reportsContainer.innerHTML = '';

    const reportsDiv = document.createElement('div');
    reportsDiv.id = 'reports-div';
    reportsDiv.className = 'info-container';

    let direct_sales = 0;
    let indirect_sales = 0;
    if (range === "month") {
        direct_sales = reports.direct_sales_month.total_revenue;
        indirect_sales = reports.indirect_sales_month.total_revenue;
    } else {
        direct_sales = reports.direct_sales_year.total_revenue;
        indirect_sales = reports.indirect_sales_year.total_revenue;
    }

    const tickets_sold = reports.tickets_sold.tickets_sold;
    const total_revenue = direct_sales + indirect_sales;
    console.log("print", direct_sales, indirect_sales, tickets_sold, total_revenue)

    const reportDiv = document.createElement('div');
    reportDiv.className = 'report';
    reportDiv.innerHTML = `
        <p>Direct Sales Revenue: $${direct_sales}</p>
        <p>Indirect Sales Revenue: $${indirect_sales}</p>
        <p>Total Revenue: $${total_revenue}</p>
        <p>Tickets Sold: ${tickets_sold}</p>
    `;
    reportsDiv.appendChild(reportDiv);

    // Append all at once to the container
    reportsContainer.appendChild(reportsDiv);
}

function drawCharts(reports) {
    console.log(reports)

    const homeContainer = document.getElementById('home-container');
    
    let chartContainer = document.getElementById('chart-container');
    if (chartContainer) {
        chartContainer.remove();
    }
    
    chartContainer = document.createElement('div');
    chartContainer.id = 'chart-container';
    homeContainer.appendChild(chartContainer);

    const canvasBar = document.createElement('canvas');
    canvasBar.id = 'bar-chart';
    chartContainer.appendChild(canvasBar);

    const barChartLabels = Object.keys(reports.tickets_sold);
    const barChartData = Object.values(reports.tickets_sold);

    console.log(barChartLabels, barChartData)

    // Bar Chart for Tickets Sold

    const ctxBar = canvasBar.getContext('2d');

    const barChart = new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: barChartLabels,
            datasets: [{
                label: 'Tickets Sold',
                data: barChartData,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    const canvasPie = document.createElement('canvas');
    canvasPie.id = 'pie-chart';
    chartContainer.appendChild(canvasPie);

    const pieChartData = [
        reports.direct_sales_month.total_revenue,
        reports.indirect_sales_month.total_revenue
    ];

    const ctxPie = canvasPie.getContext('2d');

    // Pie Chart for Sales Distribution
    const pieChart = new Chart(ctxPie, {
        type: 'pie',
        data: {
            labels: ['Direct Sales', 'Indirect Sales'],
            datasets: [{
                data: pieChartData,
                backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)'],
                borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)'],
                borderWidth: 1
            }]
        }
    });

    // Append all at once to the container
    chartContainer.appendChild(canvasBar);
    chartContainer.appendChild(canvasPie);
}
