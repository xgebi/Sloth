CREATE TABLE sloth_analytics (
	uuid character varying(200) NOT NULL PRIMARY KEY,
	pathname text NOT NULL,
	last_visit double precision
);