DROP TABLE IF EXISTS arrive;
DROP TABLE IF EXISTS depart;
DROP TABLE IF EXISTS flies;
DROP TABLE IF EXISTS operates;
DROP TABLE IF EXISTS reserved_for;
DROP TABLE IF EXISTS owns;
DROP TABLE IF EXISTS employed_by;
DROP TABLE IF EXISTS works_for;
DROP TABLE IF EXISTS purchases;
DROP TABLE IF EXISTS assist_by;
DROP TABLE IF EXISTS airport;
DROP TABLE IF EXISTS flight;
DROP TABLE IF EXISTS airline;
DROP TABLE IF EXISTS airplane;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS booking_agent;
DROP TABLE IF EXISTS ticket;
DROP TABLE IF EXISTS airline_staff;

-- airport
CREATE TABLE airport
(
  name VARCHAR(255) PRIMARY KEY NOT NULL,
  city VARCHAR(255) NOT NULL
);

-- flight
CREATE TABLE flight
(
  flight_number VARCHAR(8) PRIMARY KEY NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  status VARCHAR(255) NOT NULL
);

-- airline
CREATE TABLE airline
(
  name VARCHAR(255) PRIMARY KEY NOT NULL
);

-- airplane
CREATE TABLE airplane
(
  id INT PRIMARY KEY NOT NULL,
  seats INT NOT NULL
);

-- customer
CREATE TABLE customer
(
  email VARCHAR(255) PRIMARY KEY NOT NULL,
  name VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL,
  address VARCHAR(255) NOT NULL,
  building_number VARCHAR(255) NOT NULL,
  street VARCHAR(255) NOT NULL,
  city VARCHAR(255) NOT NULL,
  state VARCHAR(255) NOT NULL,
  phone_number VARCHAR(255) NOT NULL,
  passport_number VARCHAR(9) NOT NULL,
  passport_expiration DATE NOT NULL,
  passport_country VARCHAR(3) NOT NULL,
  dob DATE NOT NULL
);

-- booking_agent
CREATE TABLE booking_agent
(
  booking_agent_id INT PRIMARY KEY NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL
);

-- ticket
CREATE TABLE ticket
(
  ticket_id INT PRIMARY KEY NOT NULL
);

-- airline staff
CREATE TABLE airline_staff
(
  username VARCHAR(255) PRIMARY KEY NOT NULL,
  password VARCHAR(255) NOT NULL,
  first_name VARCHAR(255) NOT NULL,
  last_name VARCHAR(255) NOT NULL,
  dob DATE NOT NULL,
  permission VARCHAR(10) NOT NULL
);

-- arrive: between flight and airport
CREATE TABLE arrive
(
  flight_number VARCHAR(8),
  name VARCHAR(255),
  arrival_time TIMESTAMP NOT NULL,
  FOREIGN KEY (flight_number) REFERENCES flight(flight_number),
  FOREIGN KEY (name) REFERENCES airport(name)
);


-- depart: between flight and airport
CREATE TABLE depart
(
  flight_number VARCHAR(8),
  name VARCHAR(255),
  departure_time TIMESTAMP NOT NULL,
  FOREIGN KEY (flight_number) REFERENCES flight(flight_number),
  FOREIGN KEY (name) REFERENCES airport(name)
);

-- flies: between flight and airplane
CREATE TABLE flies
(
  airplane_id INT,
  flight_number VARCHAR(8),
  FOREIGN KEY (airplane_id) REFERENCES airplane(id),
  FOREIGN KEY (flight_number) REFERENCES flight(flight_number)
);

-- operates: between airline and flight
CREATE TABLE operates
(
  airline_name VARCHAR(255),
  flight_number VARCHAR(8),
  FOREIGN KEY (airline_name) REFERENCES airline(name),
  FOREIGN KEY (flight_number) REFERENCES flight(flight_number)
);

-- for: between ticket and flight
CREATE TABLE reserved_for
(
  ticket_id INT,
  flight_number VARCHAR(8),
  FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id),
  FOREIGN KEY (flight_number) REFERENCES flight(flight_number)
);

-- owns: between airline and airplane
CREATE TABLE owns
(
  name VARCHAR(255),
  id INT,
  FOREIGN KEY (name) REFERENCES airline(name),
  FOREIGN KEY (id) REFERENCES airplane(id)
);

-- employed_by: between booking_agent and airline
CREATE TABLE employed_by
(
  booking_agent_id INT,
  name VARCHAR(255),
  commission DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (booking_agent_id) REFERENCES booking_agent(booking_agent_id),
  FOREIGN KEY (name) REFERENCES airline(name)
);

-- works_for: between airline_staff and airline
CREATE TABLE works_for
(
  username VARCHAR(255),
  airline_name VARCHAR(255),
  FOREIGN KEY (username) REFERENCES airline_staff(username),
  FOREIGN KEY (airline_name) REFERENCES airline(name)
);

-- purchases: between customer and ticket
CREATE TABLE purchases
(
  email VARCHAR(255),
  ticket_id INT,
  FOREIGN KEY (email) REFERENCES customer(email),
  FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id)
);

-- assist_by: between booking_agent and ticket
CREATE TABLE assist_by
(
  booking_agent_id INT,
  ticket_id INT,
  commission DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (booking_agent_id) REFERENCES booking_agent(booking_agenxt_id),
  FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id)
);