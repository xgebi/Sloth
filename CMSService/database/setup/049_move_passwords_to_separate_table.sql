SELECT uuid, password INTO sloth_password FROM sloth_users;

ALTER TABLE sloth_password ADD COLUMN alg character varying(50);
UPDATE sloth_password SET alg = 'bcrypt';