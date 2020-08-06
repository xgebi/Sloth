ALTER TABLE sloth_posts ADD COLUMN imported boolean DEFAULT FALSE;
ALTER TABLE sloth_posts ADD COLUMN import_approved boolean DEFAULT FALSE;

ALTER TABLE sloth_posts ADD CONSTRAINT approval CHECK (imported OR NOT import_approved);