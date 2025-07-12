CREATE TRIGGER before_update_children
BEFORE UPDATE ON children
FOR EACH ROW
BEGIN
    DECLARE gender_text_val VARCHAR(20);
    
    -- Update gender text if gender changed
    IF NEW.gender != OLD.gender THEN
        CALL SetGenderText(NEW.gender, gender_text_val);
        SET NEW.gender_text = gender_text_val;
    END IF;
END; 