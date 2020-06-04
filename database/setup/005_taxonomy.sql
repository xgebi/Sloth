CREATE TYPE sloth_taxonomy_type AS ENUM ('category', 'tag', 'custom');

CREATE TABLE sloth_taxonomy (
	uuid character varying(200) NOT NULL,
	slug character varying(200) UNIQUE,
	display_name character varying(220),
	post_type character varying(200),
	taxonomy_type sloth_taxonomy_type NOT NULL,

	PRIMARY KEY(uuid),
	CONSTRAINT post_type_fkey FOREIGN KEY(post_type)
		REFERENCES sloth_post_types (uuid) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION

);