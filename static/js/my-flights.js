document.addEventListener('DOMContentLoaded', function () {
    // Send GET request to the server to fetch flights
    fetch('/api-my-flights', {
        method: 'GET',    
    })
    .then(response => response.json())  // Convert response to JSON
    .then(data => {
        displayFlights(data);  // Display flights in the DOM
    })
    .catch(error => {
        console.error('Error fetching the flights:', error);
        alert('Failed to fetch flights. Please try again.');
    });

    function displayFlights(flights) {
        console.log(flights)
        const flightsContainer = document.createElement('div');
        flightsContainer.id = 'flights-container';
        flightsContainer.innerHTML = '';  // Clear previous results
        document.body.appendChild(flightsContainer);

        if (flights.length === 0) {
            flightsContainer.innerHTML = '<p>No flights found.</p>';
            return;
        }

        // Create and append the elements for each flight
        flights.forEach(flight => {
            const flightDiv = document.createElement('div');
            flightDiv.className = 'flight';
            flightDiv.innerHTML = `
                <p>Flight Number: ${flight.flight_num}</p>
                <p>Status: ${flight.status}</p>
                <p>Departure Time: ${new Date(flight.depart_time).toLocaleString()}</p>
                <p>Arrival Time: ${new Date(flight.arrive_time).toLocaleString()}</p>
            `;
            flightsContainer.appendChild(flightDiv);
        });
    }
});
