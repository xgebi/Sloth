ALTER TABLE sloth_taxonomy ADD COLUMN IF NOT EXISTS lang varchar(200);

UPDATE
    sloth_taxonomy
SET lang = ss.settings_value
FROM sloth_settings as ss
WHERE ss.settings_name = 'main_language';

ALTER TABLE sloth_taxonomy
    ADD CONSTRAINT language_constraint
        FOREIGN KEY (lang)
            REFERENCES sloth_language_settings (uuid);

ALTER TABLE sloth_menus
    ADD CONSTRAINT language_constraint
        FOREIGN KEY (lang)
            REFERENCES sloth_language_settings (uuid);