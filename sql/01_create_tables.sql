USE malnutrition_db;


DROP TABLE IF EXISTS Diagnosis;
DROP TABLE IF EXISTS Measurements;
DROP TABLE IF EXISTS Children;


-- 1. Children Table
CREATE TABLE IF NOT EXISTS Children (
    child_id VARCHAR(10) PRIMARY KEY, -- Format: YYYYMMXXXX
    gender VARCHAR(10) NOT NULL,
    current_stunting_status TINYINT DEFAULT NULL,
    current_wasting_status TINYINT DEFAULT NULL
);

-- 2. Measurements Table
CREATE TABLE IF NOT EXISTS Measurements (
    measurement_id INT AUTO_INCREMENT PRIMARY KEY,
    child_id VARCHAR(10) NOT NULL,
    age_months INT NOT NULL,
    body_length_cm DECIMAL(5,2) NOT NULL,
    body_weight_kg DECIMAL(5,2) NOT NULL,
    measurement_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (child_id) REFERENCES Children(child_id)
);

-- 3. Diagnosis Table
CREATE TABLE IF NOT EXISTS Diagnosis (
    diagnosis_id INT AUTO_INCREMENT PRIMARY KEY,
    measurement_id INT NOT NULL,
    stunting_status TINYINT NOT NULL,
    wasting_status TINYINT NOT NULL,
    diagnosis_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (measurement_id) REFERENCES Measurements(measurement_id)
);