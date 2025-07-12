-- Stored Procedures for malnutrition

USE malnutrition;

DELIMITER $$

CREATE PROCEDURE GenerateChildUniqueID(OUT generated_id VARCHAR(24))
BEGIN
    SET generated_id := CONCAT(
        DATE_FORMAT(NOW(), '%Y%m%d-%H%i%s-'),
        UPPER(SUBSTRING(MD5(RAND()), 1, 4))
    );
END $$

DELIMITER ;