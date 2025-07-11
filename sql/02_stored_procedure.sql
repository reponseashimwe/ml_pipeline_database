-- Stored Procedures for malnutrition_db

USE malnutrition_db;

DELIMITER $$

CREATE PROCEDURE GenerateChildUniqueID(OUT generated_id VARCHAR(10))
BEGIN
    SET generated_id := CONCAT(
        DATE_FORMAT(CURDATE(), '%Y%m'),
        UPPER(SUBSTRING(MD5(RAND()), 1, 4))
    );
END $$

DELIMITER ;