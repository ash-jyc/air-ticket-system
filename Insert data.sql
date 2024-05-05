INSERT INTO `airline` (`name`) VALUES 
('China Eastern');

INSERT INTO `airport` (`name`, `city`) VALUES 
('JFK', 'NYC'), 
('PVG', 'Shanghai');


INSERT INTO `customer` (`email`, `name`, `password`, `building_number`, `street`, `city`, `state`, `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`) VALUES 
('zt2321@nyu.edu', 'Zhou Tianshi', '123', 'building001', 'street001', 'Shanghai', 'Shanghai', '13606161298', 'ES03123', '2033-01-01', 'China', '2000-06-030'), 
('18118922208@163.com', 'Tish', '456', 'building002', 'street002', 'Jiangyin', 'Jiangsu', '18118922208', 'EI27198', '2033-01-02', 'China', '2000-07-20');

INSERT INTO `airplane` (`id`, `name_airline`) VALUES 
('001', 'China Eastern'), 
('002', 'China Eastern');

INSERT INTO `airline_staff` (`username`, `password`, `first_name`, `last_name`, `date_of_birth`, `name_airline`) VALUES 
('Tish', '123', 'Tish', 'Zhou', '2003-06-30','China Eastern');

INSERT INTO `flight` (`flight_num`, `name_airline`,`depart_time`, `arrive_time`, `price`, `status`, `name_airplane_airline`, `plane_id`, `depart_airport`, `arrive_airport`) VALUES 
('MU521','China Eastern', '2024-01-01 00:00:00.00', '2024-01-01 10:00:00.00', 10000, 'upcoming', 'China Eastern', '001', 'JFK', 'PVG'), 
('MU522', 'China Eastern','2024-02-02 00:00:00.00', '2024-02-02 10:00:00.00', 20000, 'in_progress', 'China Eastern', '001', 'PVG', 'JFK'),
('MU523', 'China Eastern', '2024-03-03 00:00:00.00', '2024-03-03 10:00:00.00', 30000, 'delayed', 'China Eastern', '002', 'JFK', 'PVG');


INSERT INTO `booking_agent` (`email`, `password`, `booking_agent_id`) VALUES 
('123@123.com', '123', '001');

INSERT INTO `ticket` (`ticket_id`, `flight_num`) VALUES 
(1, 'MU521'), 
(2, 'MU522');


INSERT INTO `permission` (`permission_id`, `is_operator`, `is_admin`) VALUES 
(1, 0, 1);


INSERT INTO `works_for` (`airline_name`, `agent_email`) VALUES 
('China Eastern', '123@123.com');

INSERT INTO `purchase` (`ticket_id`, `customer_email`, `agent_email`, `date`) VALUES 
(1, 'zt2321@nyu.edu', NULL, '2023-01-01'), 
(2, 'zt2321@nyu.edu', '123@123.com', '2023-02-02');