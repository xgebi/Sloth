ALTER TYPE sloth_settings_type ADD VALUE 'select';

UPDATE sloth_settings SET settings_value_type = 'select' WHERE settings_name = 'main_language';
DELETE FROM sloth_settings WHERE settings_name = 'site_description';
UPDATE sloth_settings SET display_name = 'API URL' WHERE settings_name = 'api_url';