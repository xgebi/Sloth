DELETE
FROM sloth_settings
WHERE settings_name = 'sitename';

CREATE TABLE sloth_localizable_strings
(
    name text NOT NULL,
    standalone bool,

    PRIMARY KEY (name)
);

CREATE TABLE sloth_localizable_strings
(
    name text NOT NULL,
    standalone bool,

    PRIMARY KEY (name)
);

INSERT INTO sloth_localizable_strings
VALUES ('sitename', TRUE),
       ('description', TRUE),
       ('sub_headline', TRUE),
       ('archive_title', TRUE),
       ('category_title', TRUE),
       ('tag_title', TRUE),
       ('post_type_display_name', FALSE),
       ('post_type_archive_title', FALSE),
       ('post_type_category_title', FALSE),
       ('post_type_tag_title', FALSE);

CREATE TABLE sloth_localized_strings
(
    uuid      character varying(200) NOT NULL,
    name      text,
    content   text,
    lang      character varying(200) NOT NULL,
    post_type character varying(200),

    PRIMARY KEY (uuid),
    CONSTRAINT lang_fkey FOREIGN KEY (lang)
        REFERENCES sloth_language_settings (uuid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,

    CONSTRAINT name_fkey FOREIGN KEY (name)
        REFERENCES sloth_localizable_strings (name) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,

    CONSTRAINT post_type_fkey FOREIGN KEY (post_type)
        REFERENCES sloth_post_types (uuid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);