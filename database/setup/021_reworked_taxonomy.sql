CREATE TABLE sloth_post_taxonomies (
    uuid character varying(200) NOT NULL,
    post character varying(200) NOT NULL,
    taxonomy character varying(200) NOT NULL,

    PRIMARY KEY(uuid),
	CONSTRAINT post_type_fkey FOREIGN KEY(post)
		REFERENCES sloth_posts (uuid) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION,
	CONSTRAINT taxonomy_fkey FOREIGN KEY(taxonomy)
		REFERENCES sloth_taxonomy (uuid) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
)