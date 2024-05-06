document.addEventListener('DOMContentLoaded', function () {

    // default display now to next 30 days
    fetch('/api/staff-flights', {
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
        displayFlights(data);
    })
    .catch(error => {
        console.error('Error fetching the flights:', error);
        alert('Failed to fetch flights. Please try again.');
    });

    // User specify date range
    const form = document.querySelector('form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(form);
        const searchParams = new URLSearchParams();

        for (const pair of formData) {
            searchParams.append(pair[0], pair[1]);
        }

        fetch ('/api/staff-flights', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(Object.fromEntries(searchParams)),
        })
        .then(response => response.json())
        .then(data => {
            displayFlights(data);
        })
        .catch(error => {
            console.error('Error fetching the flights:', error);
            alert('Failed to fetch flights. Please try again.');
        });

    });
});

/* Display the flights */
function displayFlights(flights) {
    console.log(flights)
    const homeContainer = document.getElementById('home-container');

    let flightsContainer = document.getElementById('flights-container');
    if (flightsContainer) {
        flightsContainer.remove();
    }
    flightsContainer = document.createElement('div');
    flightsContainer.id = 'flights-container';
    flightsContainer.innerHTML = '';  // Clear previous results

    if (flights.length === 0) {
        flightsContainer.innerHTML = '<p>No flights found.</p>';
    } else {
        // Create and append the elements for each flight
        flights.forEach(flight => {
            const flightDiv = document.createElement('div');
            flightDiv.className = 'flight';
            flightDiv.innerHTML = `
            <p>Flight Number: ${flight.flight_num}</p>
            <p>Status: ${flight.status}</p>
            <p>Departure Time: ${new Date(flight.depart_time).toLocaleString()}</p>
            <p>Arrival Time: ${new Date(flight.arrive_time).toLocaleString()}</p>
            <p>Price: ¥${flight.price}</p>
        `;
            flightsContainer.appendChild(flightDiv);
        });

    }
    homeContainer.appendChild(flightsContainer);
}
