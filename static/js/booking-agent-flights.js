// Make an API call to retrieve booked flights data
fetch('/api/booked-flights')
    .then(response => response.json())
    .then(data => {
        // Display the booked flights on the page
        const homeContainer = document.getElementById('home-container');

        data.forEach(flight => {
            const flightElement = document.createElement('div');
            flightElement.className = 'flight';
            flightElement.innerHTML = `
                <p>Flight Number: ${flight.flight_num}</p>
                <p>Status: ${flight.status}</p>
                <p>Departure Time: ${new Date(flight.depart_time).toLocaleString()}</p>
                <p>Arrival Time: ${new Date(flight.arrive_time).toLocaleString()}</p>
                <p>Comission: $${flight.comission * flight.price}</p>
            `;
            homeContainer.appendChild(flightElement);
        });

        let totalComission = data.reduce((total, flight) => total + flight.comission * flight.price, 0);
        const comissionElement = document.createElement('div');
        comissionElement.innerHTML = `<p>Total Comission: $${totalComission}</p>`;
        homeContainer.appendChild(comissionElement);
    })
    .catch(error => {
        console.error('Error retrieving booked flights:', error);
    });