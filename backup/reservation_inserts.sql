DELETE FROM owns;
DELETE FROM operates;
DELETE FROM employed_by;
DELETE FROM flies;
DELETE FROM reserved_for;
DELETE FROM depart;
DELETE FROM arrive;
DELETE FROM works_for;
DELETE FROM purchases;
DELETE FROM assist_by;
DELETE FROM airline;
DELETE FROM flight;
DELETE FROM ticket;
DELETE FROM airline_staff;
DELETE FROM airplane;
DELETE FROM booking_agent;
DELETE FROM customer;
DELETE FROM airport;

-- a. One Airline name "China Eastern".
INSERT INTO airline
    (name)
VALUES
    ('China Eastern'),
    ('Japan Airlines'),
    ('Korean Air'),
    ('United Airlines'),
    ('Delta Airlines');

-- b. At least Two airports named "JFK" in NYC and "PVG" in Shanghai.
INSERT INTO airport
    (name, city)
VALUES
    ('JFK', 'NYC'),
    ('PVG', 'Shanghai'),
    ('LAX', 'Los Angeles'),
    ('HND', 'Tokyo'),
    ('ICN', 'Seoul');

-- c. Insert at least two customers with appropriate names and other attributes.
INSERT INTO customer
    (email, name, password, address, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, dob)
VALUES
    ('alicesmith55@gmail.com', 'Alice Smith', 'password123', '1234 Main St', '1234', 'Main St', 'NYC', 'NY', '1234567890', 'A123456789', '2024-09-30', 'USA', '1990-02-10'),
    ('jasonduncan@yahoo.com', 'Jason Duncan', 'DogsAreCool5678', '55 89th Ave', '55', '89th Ave', 'Shanghai', 'China', '18721279890', 'G948275837', '2032-01-01', 'CHN', '2005-05-29');

-- Insert one booking agent with appropriate name and other attributes.
INSERT INTO booking_agent
    (email, password, booking_agent_id)
VALUES
    ('jakefarmfield@gmail.com', 'password123', 1),
    ('sallyiscool123@outlook.com', 'SuperSecure889', 2);

INSERT INTO employed_by
    (booking_agent_id, name, commission)
VALUES
    (1, 'China Eastern', 10.00),
    (2, 'Japan Airlines', 20.00);

-- d. Insert at least two airplanes.
INSERT INTO airplane
    (id, seats)
VALUES
    (1, 400),
    (2, 900),
    (3, 300),
    (4, 200),
    (5, 500);

INSERT INTO owns
    (name, id)
VALUES
    ('China Eastern', 1),
    ('China Eastern', 2),
    ('China Eastern', 3),
    ('Japan Airlines', 4),
    ('Delta Airlines', 5);
-- e. Insert At least One airline Staff working for China Eastern.
INSERT INTO airline_staff
    (username, password, first_name, last_name, dob, permission)
VALUES
    ('charliebrown8', 'victoria990', 'Charlie', 'Brown', '1998-05-28', 'admin'),
    ('spongebob', 'pineapple', 'Bob', 'Johnson', '1988-11-02', 'operator');

INSERT INTO works_for
    (username, airline_name)
VALUES
    ('charliebrown8', 'China Eastern'),
    ('spongebob', 'China Eastern');

-- f. Insert several flights with upcoming, in-progress, delayed statuses.
INSERT INTO flight
    (flight_number, price, status)
VALUES
    ('MU520', 559.00, 'upcoming'),
    ('MU521', 620.00, 'in-progress'),
    ('MU522', 599.00, 'delayed');

INSERT into depart
    (flight_number, name, departure_time)
VALUES
    ('MU520', 'JFK', '2021-12-01 23:20:00'),
    ('MU521', 'PVG', '2021-12-02 11:45:00'),
    ('MU522', 'LAX', '2021-12-03 08:55:00');

INSERT INTO arrive
    (flight_number, name, arrival_time)
VALUES
    ('MU520', 'PVG', '2021-12-03 22:45:00'),
    ('MU521', 'LAX', '2021-12-02 16:15:00'),
    ('MU522', 'HND', '2021-12-04 19:25:00');

INSERT INTO operates
    (airline_name, flight_number)
VALUES
    ('China Eastern', 'MU520'),
    ('China Eastern', 'MU521'),
    ('China Eastern', 'MU522');

INSERT INTO flies
    (airplane_id, flight_number)
VALUES
    (1, 'MU520'),
    (2, 'MU521'),
    (3, 'MU522');

-- g. Insert some tickets for corresponding flights. One customer buy ticket directly
INSERT INTO ticket
    (ticket_id)
VALUES
    (1),
    (2),
    (3);

INSERT INTO reserved_for
    (ticket_id, flight_number)
VALUES
    (1, 'MU520'),
    (2, 'MU521'),
    (3, 'MU522');

INSERT INTO purchases
    (email, ticket_id)
VALUES
    ('jasonduncan@yahoo.com', 1),
    ('alicesmith55@gmail.com', 2),
    ('alicesmith55@gmail.com', 3);

-- and one customer buy ticket using a booking agent.
INSERT INTO assist_by
    (booking_agent_id, ticket_id, commission)
VALUES
    (1, 2, 10.00);
