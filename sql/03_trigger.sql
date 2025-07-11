-- Triggers for malnutrition_db

USE malnutrition_db;

DELIMITER $$

-- Trigger: BEFORE INSERT on Children
CREATE TRIGGER before_insert_children_set_id
BEFORE INSERT ON Children
FOR EACH ROW
BEGIN
    IF NEW.child_id IS NULL OR NEW.child_id = '' THEN
        CALL GenerateChildUniqueID(@new_id);
        SET NEW.child_id = @new_id;
    END IF;
END $$

-- Trigger: AFTER INSERT on Diagnosis
CREATE TRIGGER after_diagnosis_insert_update_child_status
AFTER INSERT ON Diagnosis
FOR EACH ROW
BEGIN
    DECLARE v_child_id VARCHAR(10);
    SELECT child_id INTO v_child_id FROM Measurements WHERE measurement_id = NEW.measurement_id;
    UPDATE Children
    SET current_stunting_status = NEW.stunting_status,
        current_wasting_status = NEW.wasting_status
    WHERE child_id = v_child_id;
END $$

DELIMITER ;