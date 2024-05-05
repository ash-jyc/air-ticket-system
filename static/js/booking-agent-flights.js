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
                <p>Commission: $${flight.comission * flight.price}</p>
            `;
            flightsContainer.appendChild(flightElement);
        });

        homeContainer.appendChild(flightsContainer);

        // let totalcommission = data.reduce((total, flight) => total + flight.commission * flight.price, 0);
        // const commissionElement = document.createElement('div');
        // commissionElement.innerHTML = `<p>Total commission: $${totalcommission}</p>`;
        // homeContainer.appendChild(commissionElement);
    })
    .catch(error => {
        console.error('Error retrieving booked flights:', error);
    });

// allow user to specify a range of dates to view total amount of commission received and total numbers of tickets sold

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('commission-form');
    form.addEventListener('submit', function(event) {
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
            <p>Total Commission: $${commission.total_commission.toFixed(2)}</p>
            <p>Total Tickets Sold: ${commission.total_tickets}</p>
        `;
        commissionContainer.appendChild(commissionDiv);
    }
    homeContainer.appendChild(commissionContainer);
}
