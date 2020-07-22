CREATE TABLE sloth_rss_feeds (
	uuid character varying(200) NOT NULL,
	feed text UNIQUE ,
	display_name character varying(220),
	update_frequency integer,
	last_update double precision,

	PRIMARY KEY(uuid)
);