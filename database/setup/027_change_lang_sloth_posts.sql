ALTER TABLE sloth_posts
    ALTER COLUMN lang TYPE varchar(200);

UPDATE
    sloth_posts as sp
SET lang = sls.uuid
FROM sloth_language_settings as sls
WHERE sp.lang = sls.short_name;

ALTER TABLE sloth_posts
    ADD CONSTRAINT language_constraint
        FOREIGN KEY (lang)
            REFERENCES sloth_language_settings (uuid);