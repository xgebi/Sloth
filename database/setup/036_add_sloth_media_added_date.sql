ALTER TABLE sloth_media ADD COLUMN added_date double precision;
UPDATE sloth_media SET added_date = 0 WHERE added_date IS NULL