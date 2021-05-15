CREATE TABLE sloth_libraries
(
    uuid     varchar(200) NOT NULL,
    name     text,
    version  text,
    location text UNIQUE,

    PRIMARY KEY (uuid)
);

CREATE TABLE sloth_post_libraries
(
    uuid    varchar(200),
    post    varchar(200),
    library varchar(200),

    PRIMARY KEY (uuid),
    CONSTRAINT post_fkey FOREIGN KEY (post)
        REFERENCES sloth_posts (uuid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,

    CONSTRAINT library_fkey FOREIGN KEY (library)
        REFERENCES sloth_libraries (uuid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);