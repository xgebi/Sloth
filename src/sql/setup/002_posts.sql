CREATE TABLE sloth_posts (
	uuid character varying(200) NOT NULL PRIMARY KEY,
	slug character varying(200) UNIQUE,
	title character varying(220),
	content text,
	css_file character varying(220),
	js_file character varying(220),
	publish_date double precision,
	update_date double precision,
	post_status character  varying(10),
	tags text[],
	categories text[]
);

--ALTER TABLE sloth_posts OWNER TO sloth;