CREATE TABLE sloth_tokens (
	uuid character varying(200),
	user_id character varying(200),
	user_token character varying(200),
	expiration  double precision,

	CONSTRAINT user_id_fkey FOREIGN KEY(user_id)
		REFERENCES sloth_users (uuid) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
);