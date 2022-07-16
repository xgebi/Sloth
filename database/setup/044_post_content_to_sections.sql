CREATE TYPE sloth_post_section_type AS ENUM ('text', 'python', 'r');

CREATE TABLE sloth_post_sections (
    uuid character varying(200) NOT NULL PRIMARY KEY,
    post character varying(200) NOT NULL,
    content text,
	section_type sloth_post_section_type,
	position integer,

    CONSTRAINT post_fkey FOREIGN KEY (post)
        REFERENCES sloth_posts (uuid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);
