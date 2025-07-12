USE malnutrition;

LOAD DATA LOCAL INFILE '/home/omar/ALU/student_performance_db_project/data/children.csv'
INTO TABLE Children
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(gender, current_stunting_status, current_wasting_status);

LOAD DATA LOCAL INFILE '/home/omar/ALU/student_performance_db_project/data/measurements.csv'
INTO TABLE Measurements
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(child_id, age_months, body_length_cm, body_weight_kg);

LOAD DATA LOCAL INFILE '/home/omar/ALU/student_performance_db_project/data/diagnosis.csv    '
INTO TABLE Diagnosis
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(measurement_id, stunting_status, wasting_status);