CREATE TABLE sloth_scheduled_tweets (
	uuid character varying(200) NOT NULL,
	tweet text,
	scheduled_timestamp double precision
);