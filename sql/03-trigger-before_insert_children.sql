CREATE TRIGGER before_insert_children
BEFORE INSERT ON children
FOR EACH ROW
BEGIN
    DECLARE gender_text_val VARCHAR(20);
    
    -- Generate child ID if not provided
    IF NEW.child_id IS NULL OR NEW.child_id = '' THEN
        CALL GenerateChildUniqueID(@new_id);
        SET NEW.child_id = @new_id;
    END IF;
    
    -- Set gender text
    CALL SetGenderText(NEW.gender, gender_text_val);
    SET NEW.gender_text = gender_text_val;
END; 