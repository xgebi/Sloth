CREATE TABLE sloth_categories (
	uuid character varying(200) NOT NULL PRIMARY KEY,
	slug character varying(200) UNIQUE,
	display_name character varying(220),
	post_type character varying(200)
);