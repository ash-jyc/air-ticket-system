CREATE TABLE `booking_agent` (
  `email` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) DEFAULT NULL,
  `booking_agent_id` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`email`)
);

CREATE TABLE `airline` (
  `name` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`name`)
);

CREATE TABLE `airline_staff` (
  `username` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) DEFAULT NULL,
  `first_name` VARCHAR(255) DEFAULT NULL,
  `last_name` VARCHAR(255) DEFAULT NULL,
  `date_of_birth` DATE DEFAULT NULL,
  `name_airline` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`username`),
  FOREIGN KEY (`name_airline`) REFERENCES `airline`(`name`)
);

CREATE TABLE `airplane` (
  `id` VARCHAR(255) NOT NULL,
  `name_airline` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`name_airline`) REFERENCES `airline`(`name`)
);

CREATE TABLE `airport` (
  `name` VARCHAR(255) NOT NULL,
  `city` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`name`)
);

CREATE TABLE `customer` (
  `email` VARCHAR(255) NOT NULL,
  `name` VARCHAR(255) DEFAULT NULL,
  `password` VARCHAR(255) DEFAULT NULL,
  `building_number` VARCHAR(255) DEFAULT NULL,
  `street` VARCHAR(255) DEFAULT NULL,
  `city` VARCHAR(255) DEFAULT NULL,
  `state` VARCHAR(255) DEFAULT NULL,
  `phone_number` VARCHAR(255) DEFAULT NULL,
  `passport_number` VARCHAR(255) DEFAULT NULL,
  `passport_expiration` DATE DEFAULT NULL,
  `passport_country` VARCHAR(255) DEFAULT NULL,
  `date_of_birth` DATE DEFAULT NULL,
  PRIMARY KEY (`email`)
);

CREATE TABLE `flight` (
  `flight_num` VARCHAR(255) NOT NULL,
  `name_airline` VARCHAR(255) NOT NULL,
  `depart_time` DATETIME(6) DEFAULT NULL,
  `arrive_time` DATETIME(6) DEFAULT NULL,
  `price` FLOAT DEFAULT NULL,
  `status` VARCHAR(255) DEFAULT NULL,
  `name_airplane_airline` VARCHAR(255) NOT NULL,
  `plane_id` VARCHAR(255) NOT NULL,
  `depart_airport` VARCHAR(255) NOT NULL,
  `arrive_airport` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`flight_num`),
  FOREIGN KEY (`name_airline`) REFERENCES `airline`(`name`),
  FOREIGN KEY (`name_airplane_airline`) REFERENCES  `airplane`(`name_airline`),
  FOREIGN KEY (`plane_id`) REFERENCES `airplane`(`id`),
  FOREIGN KEY (`depart_airport`) REFERENCES `airport`(`name`),
  FOREIGN KEY (`arrive_airport`) REFERENCES `airport`(`name`)
);

CREATE TABLE `permission` (
  `permission_id` INT NOT NULL AUTO_INCREMENT,
  `is_operator` BOOLEAN NOT NULL,
  `is_admin` BOOLEAN NOT NULL,
  PRIMARY KEY (`permission_id`)
);

CREATE TABLE `have_permission` (
  `permission_id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`permission_id`,`username`),
  FOREIGN KEY (`permission_id`) REFERENCES `permission`(`permission_id`),
  FOREIGN KEY (`username`) REFERENCES `airline_staff`(`username`)
);

CREATE TABLE `ticket` (
  `ticket_id` INT NOT NULL AUTO_INCREMENT,
  `flight_num` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`ticket_id`),
  FOREIGN KEY (`flight_num`) REFERENCES `flight`(`flight_num`)
);

CREATE TABLE `works_for` (
  `agent_email` VARCHAR(255) NOT NULL,
  `airline_name` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`agent_email`, `airline_name`),
  FOREIGN KEY (`agent_email`) REFERENCES `booking_agent`(`email`),
  FOREIGN KEY (`airline_name`) REFERENCES `airline`(`name`)
);

CREATE TABLE `purchase` (
  `ticket_id` INT NOT NULL AUTO_INCREMENT,
  `customer_email` VARCHAR(255) NOT NULL,
  `agent_email` VARCHAR(255) DEFAULT NULL,
  `date` DATE DEFAULT NULL,
  PRIMARY KEY (`ticket_id`,`customer_email`),
  FOREIGN KEY (`ticket_id`) REFERENCES `ticket`(`ticket_id`),
  FOREIGN KEY (`customer_email`) REFERENCES `customer`(`email`),
  FOREIGN KEY (`agent_email`) REFERENCES `booking_agent`(`email`)
);