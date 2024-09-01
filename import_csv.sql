-- import data from a CSV file
USE kpi;
LOAD DATA INFILE '/var/lib/mysql-files/ACB20230411'
INTO TABLE flights
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
(arrived_at, flight_id, origin, destination, route);
