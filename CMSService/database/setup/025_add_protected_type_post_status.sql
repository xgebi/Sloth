ALTER TYPE sloth_post_status ADD VALUE 'protected' AFTER 'scheduled';
ALTER TABLE sloth_posts ADD COLUMN password varchar(250);