CREATE TYPE sloth_menu_item_types AS ENUM ('custom', 'post');

CREATE TABLE sloth_menu_items (
    uuid character varying(200),
    menu character varying(200),
    title text,
    type sloth_menu_item_types,
    url text,

    PRIMARY KEY(uuid),
    CONSTRAINT menu_fkey FOREIGN KEY(menu)
		REFERENCES sloth_menus (uuid) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
);