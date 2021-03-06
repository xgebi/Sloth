CREATE TYPE sloth_post_status AS ENUM ('published', 'draft', 'deleted', 'scheduled');

CREATE TABLE sloth_posts (
	uuid character varying(200) NOT NULL,
	original_lang_entry_uuid character varying(200),
	lang character varying(5) NOT NULL,
	slug character varying(200) UNIQUE,
	post_type character varying(200),
	author character varying(200) NULL,
	title character varying(220),
	content text,
	excerpt text,
	css text,
	use_theme_css boolean DEFAULT TRUE,
	js text,
	use_theme_js boolean DEFAULT TRUE,
	thumbnail character varying(200) NULL,
	publish_date double precision,
	update_date double precision,
	post_status sloth_post_status,
	tags text[],
	categories text[],

	PRIMARY KEY(uuid),
	CONSTRAINT post_type_fkey FOREIGN KEY(post_type)
		REFERENCES sloth_post_types (uuid) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION,
	CONSTRAINT author_fkey FOREIGN KEY(author)
		REFERENCES sloth_users (uuid) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION,
	CONSTRAINT thumbnail_fkey FOREIGN KEY(thumbnail)
		REFERENCES sloth_media (uuid) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
);