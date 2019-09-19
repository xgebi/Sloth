CREATE TABLE sloth_media (
	uuid character varying(200) NOT NULL,
	file_path text UNIQUE,
	alt text,
	wp_id integer UNIQUE,

	PRIMARY KEY(uuid)
)