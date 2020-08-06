CREATE TABLE sloth_menus (
    uuid character varying(200),
    name text UNIQUE,

    PRIMARY KEY(uuid)
);