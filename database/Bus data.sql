-- Bus Tracking System — MySQL Schema

CREATE DATABASE IF NOT EXISTS bus_tracker;
USE bus_tracker;

CREATE TABLE Routes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE buses (
    id VARCHAR(20) PRIMARY KEY,          -- e.g. 'bus-1'
    route_id INT NOT NULL,
    driver_name VARCHAR(100),
    FOREIGN KEY (route_id) REFERENCES Routes(id)
);

CREATE TABLE stops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    lat DOUBLE NOT NULL,
    lng DOUBLE NOT NULL,
    stop_order INT NOT NULL,             -- sequence along the route, starting at 1
    FOREIGN KEY (route_id) REFERENCES Routes(id)
);

CREATE TABLE bus_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bus_id VARCHAR(20) NOT NULL,
    lat DOUBLE NOT NULL,
    lng DOUBLE NOT NULL,
    recorded_at DATETIME NOT NULL,
    FOREIGN KEY (bus_id) REFERENCES buses(id),
    INDEX idx_bus_time (bus_id, recorded_at)
);

-- ---------------------------------------------------------------------------
-- Sample seed data — replace coordinates with your actual campus route
-- ---------------------------------------------------------------------------
INSERT INTO Routes (id, name) VALUES (1, 'Route A');

INSERT INTO buses (id, route_id, driver_name) VALUES ('bus-1', 1, 'Ramesh Kumar');

INSERT INTO stops (route_id, name, lat, lng, stop_order) VALUES
    (1, 'Main Gate',        30.3165, 78.0322, 1),
    (1, 'City Center',      30.3210, 78.0410, 2),
    (1, 'Clock Tower',      30.3255, 78.0480, 3),
    (1, 'Railway Station',  30.3300, 78.0560, 4),
    (1, 'College Campus',   30.3350, 78.0640, 5);

SELECT COUNT(*) FROM stops;         -- expect 8 (5 route-1 + 3 route-2)
SELECT COUNT(*) FROM bus_locations; -- expect 11 (8 for bus-1 + 3 for bus-2)
SELECT COUNT(*) FROM routes;        -- expect 2
SELECT COUNT(*) FROM buses;         -- expect 2
SHOW TABLES;                        -- trip_history bhi list mein honi chahiye

INSERT INTO bus_locations
VALUES (3,'bus-2', 35.3400, 78.9300, NOW());

SELECT * 
FROM bus_locations
ORDER BY recorded_at DESC
LIMIT 5;