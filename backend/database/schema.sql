-- Bus Tracking System — Schema
-- This is the CURRENT, complete schema (includes the paired_route_id
-- column for bidirectional routes — you don't need to separately run
-- the old add_return_route.sql migration if you're setting up fresh).

CREATE DATABASE IF NOT EXISTS bus_tracker;
USE bus_tracker;

CREATE TABLE routes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    paired_route_id INT NULL   -- links a route to its opposite-direction counterpart
);

CREATE TABLE buses (
    id VARCHAR(50) PRIMARY KEY,       -- e.g. 'bus-1'
    bus_number VARCHAR(50) NOT NULL,  -- e.g. 'Bus 01' (display name)
    route_id INT NOT NULL,
    FOREIGN KEY (route_id) REFERENCES routes(id)
);

CREATE TABLE stops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    lat DECIMAL(10, 7) NOT NULL,
    lng DECIMAL(10, 7) NOT NULL,
    stop_order INT NOT NULL,          -- sequence along the route, starting at 1
    FOREIGN KEY (route_id) REFERENCES routes(id)
);

CREATE TABLE bus_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bus_id VARCHAR(50) NOT NULL,
    lat DECIMAL(10, 7) NOT NULL,
    lng DECIMAL(10, 7) NOT NULL,
    recorded_at DATETIME NOT NULL,
    FOREIGN KEY (bus_id) REFERENCES buses(id),
    INDEX idx_bus_time (bus_id, recorded_at)
);

-- ---------------------------------------------------------------------------
-- Sample seed data — replace with your actual campus route.
-- ---------------------------------------------------------------------------
INSERT INTO routes (name) VALUES ('College Main Route');

INSERT INTO buses (id, bus_number, route_id) VALUES ('bus-1', 'Bus 01', 1);

INSERT INTO stops (route_id, name, lat, lng, stop_order) VALUES
    (1, 'College Gate',   30.3426, 77.9250, 1),
    (1, 'Clock Tower',    30.3256, 78.0437, 2),
    (1, 'ISBT',           30.2881, 77.9990, 3);

-- Starting GPS point so /api/bus-location doesn't 404 before a driver
-- or the simulate_movement.py script sends real updates.
INSERT INTO bus_locations (bus_id, lat, lng, recorded_at)
VALUES ('bus-1', 30.3426, 77.9250, NOW());

-- ---------------------------------------------------------------------------
-- Return-direction route — mirrors the stops above in reverse order.
-- Lets a bus travel the route both ways (see /api/buses/<id>/toggle-direction).
-- ---------------------------------------------------------------------------
INSERT INTO routes (name) VALUES ('College Main Route (Return)');

INSERT INTO stops (route_id, name, lat, lng, stop_order)
SELECT
    (SELECT id FROM routes WHERE name = 'College Main Route (Return)'),
    name, lat, lng,
    (SELECT COUNT(*) FROM stops WHERE route_id = 1) - stop_order + 1
FROM stops
WHERE route_id = 1
ORDER BY stop_order;

UPDATE routes SET paired_route_id = (SELECT id FROM routes WHERE name = 'College Main Route (Return)')
WHERE id = 1;

UPDATE routes SET paired_route_id = 1
WHERE name = 'College Main Route (Return)';
