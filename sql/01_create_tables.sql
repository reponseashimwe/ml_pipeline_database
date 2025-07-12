CREATE DATABASE IF NOT EXISTS malnutrition_db;
USE malnutrition_db;

-- Drop tables if they exist (in reverse dependency order)
DROP TABLE IF EXISTS Diagnosis;
DROP TABLE IF EXISTS Measurements;
DROP TABLE IF EXISTS Children;

-- Children table
CREATE TABLE Children (
    child_id INT AUTO_INCREMENT PRIMARY KEY,
    gender VARCHAR(20) NOT NULL,
    current_stunting_status TINYINT,
    current_wasting_status TINYINT
);

-- Measurements table
CREATE TABLE Measurements (
    measurement_id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    age_months INT NOT NULL,
    body_length_cm DECIMAL(5,2) NOT NULL,
    body_weight_kg DECIMAL(5,2) NOT NULL,

    FOREIGN KEY (child_id) REFERENCES Children(child_id)
);

-- Diagnosis table
CREATE TABLE Diagnosis (
    diagnosis_id INT AUTO_INCREMENT PRIMARY KEY,
    measurement_id INT NOT NULL,
    stunting_status TINYINT NOT NULL,
    wasting_status TINYINT NOT NULL,
    FOREIGN KEY (measurement_id) REFERENCES Measurements(measurement_id)
);