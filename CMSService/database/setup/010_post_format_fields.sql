CREATE TABLE sloth_post_format_fields (
	uuid character varying(200) NOT NULL,
	display_name character varying(220),
	post_format character varying(200),
	field_type character varying(220),

	PRIMARY KEY(uuid),
	CONSTRAINT post_format_fkey FOREIGN KEY(post_format)
		REFERENCES sloth_post_formats (uuid) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION

);