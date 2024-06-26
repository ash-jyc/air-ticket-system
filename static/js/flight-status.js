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
        fetch('/api/flight-status', {
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
        // check if the flights container already exists
        let flightsContainer = document.getElementById('home-page');
        if (flightsContainer) {
            flightsContainer.remove();
        }

        flightsContainer = document.createElement('div');
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
