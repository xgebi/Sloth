CREATE TABLE sloth_users (
	uuid character varying(200) NOT NULL PRIMARY KEY,
	username character varying(50) UNIQUE,
	display_name character varying(100),
	password character varying(500),
	email character varying(350),
	token character varying(350),
	expiry_date double precision,
	permissions_level integer DEFAULT 0 NOT NULL
);


--ALTER TABLE sloth_users OWNER TO sloth;