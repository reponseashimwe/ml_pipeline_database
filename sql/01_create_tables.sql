USE malnutrition;

DROP TABLE IF EXISTS Diagnosis;
DROP TABLE IF EXISTS Measurements;
DROP TABLE IF EXISTS Children;

-- 1. Children Table
CREATE TABLE IF NOT EXISTS Children (
    child_id VARCHAR(24) PRIMARY KEY, -- Format: YYYYMMDD-HHMMSS-XXXX
    gender VARCHAR(10) NOT NULL,
    gender_text VARCHAR(20) NOT NULL, -- "Male" or "Female"
    current_stunting_status VARCHAR(50) DEFAULT NULL,
    current_wasting_status VARCHAR(50) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Measurements Table
CREATE TABLE IF NOT EXISTS Measurements (
    measurement_id INT AUTO_INCREMENT PRIMARY KEY,
    child_id VARCHAR(24) NOT NULL,
    age_months INT NOT NULL,
    body_length_cm DECIMAL(5,2) NOT NULL,
    body_weight_kg DECIMAL(5,2) NOT NULL,
    measurement_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (child_id) REFERENCES Children(child_id) ON DELETE CASCADE
);

-- 3. Diagnosis Table
CREATE TABLE IF NOT EXISTS Diagnosis (
    diagnosis_id INT AUTO_INCREMENT PRIMARY KEY,
    measurement_id INT NOT NULL,
    stunting_status VARCHAR(50) NOT NULL,
    wasting_status VARCHAR(50) NOT NULL,
    diagnosis_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (measurement_id) REFERENCES Measurements(measurement_id) ON DELETE CASCADE
);