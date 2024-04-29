-- a. Show all the upcoming flights in the system
SELECT *
FROM flight
WHERE status='upcoming';

-- b. Show all of the delayed flights in the system.
SELECT *
FROM flight
WHERE status='delayed';

-- c. Show the customer names who used booking agent to buy the tickets.
SELECT c.name
FROM customer c 
JOIN purchases p ON c.email = p.email 
JOIN ticket t ON p.ticket_id = t.ticket_id
WHERE t.ticket_id IN (
    SELECT ticket_id
    FROM assist_by
);

-- d. Show all of the airplanes owned by the airline (such as "Emirates")
SELECT airline.name, a.id
FROM airline
JOIN owns o ON airline.name = o.name
JOIN airplane a ON o.id = a.id