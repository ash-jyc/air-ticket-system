document.addEventListener('DOMContentLoaded', function () {
    // Send GET request to the server to fetch flights
    fetch('/api/my-flights', {
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
        const homeContainer = document.getElementById('home-container');
        const flightsContainer = document.createElement('div');
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
                <p>Price: $${flight.price}</p>
            `;
                flightsContainer.appendChild(flightDiv);
            });

            const totalSpending = flights.reduce((total, flight) => total + flight.price, 0);
            const spendingDiv = document.createElement('div');
            spendingDiv.innerHTML = `<p>Total Spending: $${totalSpending}</p>`;
            flightsContainer.appendChild(spendingDiv);
        }
        homeContainer.appendChild(flightsContainer);
    }

    fetch('/api/track-spending', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(data => {
            console.log('Fetched spending data:', data);
            displaySpending(data);
        })
        .catch(error => {
            console.error('Error fetching the spending:', error);
            alert('Failed to fetch spending. Please try again.');
        });
    
    function displaySpending(spending) {
        const homeContainer = document.getElementById('home-container');  // Ensure this exists in your HTML
        const spendingContainer = document.createElement('div');
        spendingContainer.id = 'spending-container';
        spendingContainer.innerHTML = '';  // Clear previous results
    
        if (spending.length === 0) {
            spendingContainer.innerHTML = '<p>No spending found.</p>';
        } else {
            // Calculate total spending from all fetched data
            const totalSpending = spending.reduce((total, spend) => total + parseFloat(spend.total_spent), 0).toFixed(2);
            const spendingDiv = document.createElement('div');
            spendingDiv.innerHTML = `<p>Total Spending: $${totalSpending}</p>`;
            spendingContainer.appendChild(spendingDiv);
    
            const canvas = document.createElement('canvas');
            canvas.id = 'spendingChart';
            spendingContainer.appendChild(canvas);
    
            const months = spending.map(spend => spend.month);
            const amounts = spending.map(spend => spend.total_spent);
    
            const ctx = canvas.getContext('2d');
            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: months,
                    datasets: [{
                        label: 'Monthly Spending',
                        data: amounts,
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
        }
        homeContainer.appendChild(spendingContainer);
    }
    

});
