document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/top-customers-year', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(data => {
            displayCustomers(data, "This Year");
        })
        .catch(error => {
            console.error('Error fetching the customers:', error);
            alert('Failed to fetch customers. Please try again.');
        });

});

function displayCustomers(customers, timePeriod) {
    console.log(timePeriod)
    console.log(customers)
    const topCustomersContainer = document.getElementById('top-customers-container');
    
    if (timePeriod === "") {
        topCustomersContainer.innerHTML = "";
    }

    const customersContainer = document.createElement('div');
    customersContainer.id = 'customers-container';
    customersContainer.className = 'info-container';
    customersContainer.innerHTML = '';  // Clear previous results

    // Create and append the elements for each agent
    customers.forEach((customer, i) => {
        console.log(customer, i)
        const customerDiv = document.createElement('div');
        customerDiv.className = 'customer';
        customerDiv.innerHTML = `
            <p>✨ Rank: ${i + 1} ✨</p>
            <p>Name: ${customer.name}</p>
            <p>Email: ${customer.email}</p>
            <p>Number of tickets: ${customer.tickets_purchased}</p>
        `;
        console.log(customerDiv)
        customersContainer.appendChild(customerDiv);
    });

    topCustomersContainer.appendChild(customersContainer);
}