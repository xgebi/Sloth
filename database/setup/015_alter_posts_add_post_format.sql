ALTER TABLE sloth_posts ADD COLUMN post_format character varying(200);

ALTER TABLE sloth_posts ADD CONSTRAINT post_format_fkey FOREIGN KEY(post_format)
		REFERENCES sloth_post_formats (uuid) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION