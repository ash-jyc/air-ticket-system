document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('searchForm');
    form.addEventListener('submit', function(event) {
        event.preventDefault();  // Prevent the default form submission

        const customerEmail = document.getElementById('customer_email').value;
        const flightNumber = new URLSearchParams(window.location.search).get('flight_number');

        fetch('/api/book-with-agent', {
            method: 'POST',
            body: JSON.stringify({ customer_email: customerEmail, flight_number: flightNumber }),
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            alert('Flight booked successfully!');
            window.location = '/my-flights';
        })
        .catch(error => {
            console.error('Error booking the flight:', error);
            alert('Failed to book the flight. Please try again.');
        });
    });
});
