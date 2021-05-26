CREATE TABLE sloth_forms
(
    uuid varchar(200) NOT NULL,
    name text,
    slug text         NOT NULL,
    lang varchar(200) NOT NULL,

    PRIMARY KEY (uuid),
    CONSTRAINT lang_fkey FOREIGN KEY (lang)
        REFERENCES sloth_language_settings (uuid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

CREATE TABLE sloth_form_fields
(
    uuid varchar(200) NOT NULL,
    name text         NOT NULL,
    form varchar(200),

    PRIMARY KEY (uuid),
    CONSTRAINT form_fkey FOREIGN KEY (form)
        REFERENCES sloth_forms (uuid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);