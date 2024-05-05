document.addEventListener('DOMContentLoaded', function () {
    // Make an API call to retrieve booked flights data
    fetch('/api/booked-flights')
        .then(response => response.json())
        .then(data => {
            // Display the booked flights on the page
            const homeContainer = document.getElementById('home-container');
            const flightsContainer = document.createElement('div');
            flightsContainer.id = 'flights-container';
            flightsContainer.innerHTML = '';  // Clear previous results

            data.forEach(flight => {
                const flightElement = document.createElement('div');
                flightElement.className = 'flight';
                flightElement.innerHTML = `
            <p>Flight Number: ${flight.flight_num}</p>
            <p>Status: ${flight.status}</p>
            <p>Departure Time: ${new Date(flight.depart_time).toLocaleString()}</p>
            <p>Arrival Time: ${new Date(flight.arrive_time).toLocaleString()}</p>
            <p>Commission: ¥${flight.comission * flight.price}</p>
        `;
                flightsContainer.appendChild(flightElement);
            });

            homeContainer.appendChild(flightsContainer);

        })
        .catch(error => {
            console.error('Error retrieving booked flights:', error);
        });

    // allow user to specify a range of dates to view total amount of commission received and total numbers of tickets sold
    const form = document.getElementById('commission-form');
    form.addEventListener('submit', function (event) {
        event.preventDefault();  // Prevent the default form submission

        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        fetch('/api/track-commission', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
            .then(response => response.json())
            .then(data => {
                console.log('Fetched commission data:', data);
                displayCommission(data);
            })
            .catch(error => {
                console.error('Error fetching the commission:', error);
                alert('Failed to fetch commission. Please try again.');
            });
    });
    function displayCommission(commission) {
        const homeContainer = document.getElementById('home-container');

        let commissionContainer = document.getElementById('commission-container');
        if (commissionContainer) {
            commissionContainer.remove();
        }

        commissionContainer = document.createElement('div');
        commissionContainer.id = 'commission-container';
        commissionContainer.innerHTML = '';

        if (!commission.total_commission && !commission.total_tickets) {
            commissionContainer.innerHTML = '<p>No commission data available for the selected period.</p>';
        } else {
            const commissionDiv = document.createElement('div');
            commissionDiv.className = 'commission';
            commissionDiv.innerHTML = `
                <p>Total Commission: ¥${commission.total_commission.toFixed(2)}</p>
                <p>Total Tickets Sold: ${commission.total_tickets}</p>
            `;
            commissionContainer.appendChild(commissionDiv);
        }
        homeContainer.appendChild(commissionContainer);
    }


    fetch('/api/top-customers')
        .then(response => response.json())
        .then(data => {
            console.log('Fetched top customers data:', data);
            createChart('ticketsChart', 'Tickets Bought',
                        data.top_tickets.map(item => `${item[1]} (${item[0]})`),
                        data.top_tickets.map(item => item[2]));
            createChart('commissionChart', 'Commission Earned',
                        data.top_commissions.map(item => `${item[1]} (${item[0]})`),
                        data.top_commissions.map(item => item[2]));
        })
        .catch(error => console.error('Error loading top customers data:', error));

    function createChart(canvasId, label, labels, data) {
        console.log('Creating chart:', canvasId, label, labels, data);
        const homeContainer = document.getElementById('home-container');
        const chartContainer = document.createElement('div');
        chartContainer.id = canvasId + '-container';
        chartContainer.innerHTML = '';

        if (labels.length === 0) {
            chartContainer.innerHTML = `<p>No ${label.toLowerCase()} data available.</p>`;
        } else {
            const canvas = document.createElement('canvas');
            canvas.id = canvasId;
            chartContainer.appendChild(canvas);

            const ctx = canvas.getContext('2d');

            // Instantiate a new chart and store its reference in the window object
            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: label,
                        data: data,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: { // Use 'y' for the y-axis as per new Chart.js version syntax
                            beginAtZero: true
                        }
                    },
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }

        homeContainer.appendChild(chartContainer);
    }
});