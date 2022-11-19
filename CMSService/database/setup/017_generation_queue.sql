CREATE TABLE sloth_generation_queue (
    uuid character varying(200) NOT NULL,
    all_posts boolean,
	post_uuid character varying(200) NOT NULL,
	timedate_added double precision,

	PRIMARY KEY(uuid)
);