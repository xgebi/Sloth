CREATE TABLE settings (
    settings_name       VARCHAR(40) PRIMARY KEY,
    display_name        VARCHAR(100) NOT NULL,
    settings_value      VARCHAR(255) NOT NULL,
    section_id          VARCHAR(40) NOT NULL,
    setting_type        VARCHAR(100) NOT NULL DEFAULT "core",
    section_name        VARCHAR(60) NOT NULL
);
