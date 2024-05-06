document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/top-agents-year', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(data => {
            displayCustomers(data, "This Year");
        })
        .catch(error => {
            console.error('Error fetching the agents:', error);
            alert('Failed to fetch agents. Please try again.');
        });

    fetch('/api/top-agents-month', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(data => {
            displayCustomers(data, "This Month");
        })
        .catch(error => {
            console.error('Error fetching the agents:', error);
            alert('Failed to fetch agents. Please try again.');
        });
    
    const form = document.querySelector('form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();  // Prevent the default form submission

        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        console.log(data)

        fetch('/api/top-agents-spec', {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then(response => response.json())
            .then(data => {
                displayCustomers(data, "");
            })
            .catch(error => {
                console.error('Error fetching the agents:', error);
                alert('Failed to fetch agents. Please try again.');
            });
    });
});

function displayCustomers(agents, timePeriod) {
    console.log(timePeriod)
    console.log(agents)
    const topAgentsContainer = document.getElementById('top-agents-container');
    
    if (timePeriod === "") {
        topAgentsContainer.innerHTML = "";
    }

    const agentsContainer = document.createElement('div');
    agentsContainer.id = 'agents-container';
    agentsContainer.className = 'info-container';
    agentsContainer.innerHTML = '';  // Clear previous results

    // Create and append the elements for each agent
    agents.forEach((agent, i) => {
        console.log(agent, i)
        const agentDiv = document.createElement('div');
        agentDiv.className = 'agent';
        agentDiv.innerHTML = `
            <p>✨ Rank: ${i + 1} ✨</p>
            <p>Agent ID: ${agent.booking_agent_id}</p>
            <p>Email: ${agent.email}</p>
            <p>Commission earned: ¥${agent.commission_earned.toFixed(2)}</p>
        `;
        console.log(agentDiv)
        agentsContainer.appendChild(agentDiv);
    });

    const topAgentTitle = document.createElement('h2');
    topAgentTitle.innerHTML = 'Top Booking Agents ' + timePeriod;
    topAgentTitle.className = 'top-agent-title';
    
    topAgentsContainer.appendChild(topAgentTitle);
    topAgentsContainer.appendChild(agentsContainer);
}