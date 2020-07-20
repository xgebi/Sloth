CREATE TABLE sloth_language_settings (
	uuid character varying(200) NOT NULL PRIMARY KEY,
	short_name VARCHAR(10) UNIQUE NOT NULL,
	long_name text NOT NULL
);