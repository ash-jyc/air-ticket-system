document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();  // Prevent the default form submission

        const formData = new FormData(form);
        const searchParams = new URLSearchParams();

        // Append form data into searchParams for sending
        for (const pair of formData) {
            searchParams.append(pair[0], pair[1]);
        }

        // Send POST request to the server with the form data
        fetch('/flight-status', {
            method: 'POST',
            body: searchParams,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        })
        .then(response => response.json())  // Convert response to JSON
        .then(data => {
            displayFlights(data);  // Display flights in the DOM
        })
        .catch(error => {
            console.error('Error fetching the flights:', error);
            alert('Failed to fetch flights. Please try again.');
        });
    });

    function displayFlights(flights) {
        console.log(flights)
        const flightsContainer = document.getElementById('flights');
        flightsContainer.innerHTML = '';  // Clear previous results

        if (flights.length === 0) {
            flightsContainer.innerHTML = '<p>No flights found.</p>';
            return;
        }

        // Create and append the elements for each flight
        flights.forEach(flight => {
            const flightDiv = document.createElement('div');
            flightDiv.className = 'flight';
            flightDiv.innerHTML = `
                <p>Flight Number: ${flight.flight_number}</p>
                <p>Status: ${flight.status}</p>
                <p>Departure Time: ${new Date(flight.departure_time).toLocaleString()}</p>
                <p>Arrival Time: ${new Date(flight.arrival_time).toLocaleString()}</p>
            `;
            flightsContainer.appendChild(flightDiv);
        });
    }
});
