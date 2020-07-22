CREATE TABLE sloth_post_formats (
	uuid character varying(200) NOT NULL,
	feed character varying(200),
	link text,
	read boolean,
	read_timestamp double precision,
	added_timestamp double precision,

	PRIMARY KEY(uuid),
	CONSTRAINT post_type_fkey FOREIGN KEY(feed)
		REFERENCES sloth_rss_feeds (uuid) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION

);