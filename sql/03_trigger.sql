-- Triggers for malnutrition

USE malnutrition;

DELIMITER $$

CREATE TRIGGER before_insert_children_set_id_and_text
BEFORE INSERT ON Children
FOR EACH ROW
BEGIN
    DECLARE gender_text_val VARCHAR(20);
    -- Generate child ID if not provided
    IF NEW.child_id IS NULL OR NEW.child_id = '' THEN
        CALL GenerateChildUniqueID(@new_id);
        SET NEW.child_id = @new_id;
    END IF;
    -- Set gender text
    IF NEW.gender = 'Laki-laki' THEN
        SET gender_text_val := 'Male';
    ELSEIF NEW.gender = 'Perempuan' THEN
        SET gender_text_val := 'Female';
    ELSE
        SET gender_text_val := 'Unknown';
    END IF;
    SET NEW.gender_text = gender_text_val;
END $$

DELIMITER ;