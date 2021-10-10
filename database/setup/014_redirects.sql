CREATE TABLE sloth_redirects (
	uuid character varying(200) NOT NULL,
	old_url text,
	new_url text,

	PRIMARY KEY(uuid)
);