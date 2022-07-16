ALTER TABLE sloth_form_fields ADD COLUMN is_childless boolean NOT NULL DEFAULT FALSE;

CREATE TABLE sloth_form_fields_children
(
    uuid varchar(200),
    field varchar(200) NOT NULL,
    name text,
    value text NOT NULL,

    PRIMARY KEY (uuid),
    CONSTRAINT field_fkey FOREIGN KEY (field)
        REFERENCES sloth_form_fields (uuid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);