CREATE TABLE sloth_post_format_fields_values (
	uuid character varying(200) NOT NULL,
	post_format_field character varying(200),
	field_value text,

	PRIMARY KEY(uuid),
	CONSTRAINT post_format_fkey FOREIGN KEY(post_format_field)
		REFERENCES sloth_post_format_fields (uuid) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION

);