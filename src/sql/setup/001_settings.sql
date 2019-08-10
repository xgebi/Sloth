CREATE TYPE sloth_settings_type AS ENUM ('boolean', 'text');

CREATE TABLE sloth_settings (
	settings_name			VARCHAR(80) PRIMARY KEY,
	display_name			VARCHAR(100) NOT NULL,
	settings_value_type		sloth_settings_type NOT NULL,
	settings_type			VARCHAR(80) NOT NULL,
	settings_value			VARCHAR(200) NOT NULL
);

COMMENT ON COLUMN sloth_settings.settings_name IS 'Name of the setting in alphanumeric and underscores';
COMMENT ON COLUMN sloth_settings.display_name IS 'Human readable name of setting';
COMMENT ON COLUMN sloth_settings.settings_value_type IS 'Indicator for how front-end should render setting';
COMMENT ON COLUMN sloth_settings.settings_type IS 'Indicates if setting belongs to SlothCMS, theme or plugin'; 
COMMENT ON COLUMN sloth_settings.settings_value IS 'Actual value of the settings';