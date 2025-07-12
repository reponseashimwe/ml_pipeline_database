CREATE PROCEDURE SetGenderText(IN gender_value VARCHAR(10), OUT gender_text_value VARCHAR(20))
BEGIN
    IF gender_value = 'Laki-laki' THEN
        SET gender_text_value := 'Male';
    ELSEIF gender_value = 'Perempuan' THEN
        SET gender_text_value := 'Female';
    ELSE
        SET gender_text_value := 'Unknown';
    END IF;
END; 