CREATE TABLE sloth_post_types (
	uuid character varying(200) NOT NULL PRIMARY KEY,
	slug character varying(200) UNIQUE,
	display_name character varying(220),
	tags_enabled boolean,
	categories_enabled boolean,
    archive_enabled boolean
);