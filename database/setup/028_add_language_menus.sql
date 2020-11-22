ALTER TABLE sloth_menus
    ADD COLUMN IF NOT EXISTS lang varchar(200);

UPDATE
    sloth_settings as ss
SET settings_value = sls.uuid
FROM sloth_language_settings as sls
WHERE ss.settings_value = sls.short_name
  AND ss.settings_name = 'main_language';

UPDATE
    sloth_menus as sm
SET lang = ss.settings_value
FROM sloth_settings as ss
WHERE ss.settings_name = 'main_language';