ALTER TABLE sloth_messages DROP COLUMN body;
ALTER TABLE sloth_messages DROP COLUMN name;
ALTER TABLE sloth_messages DROP COLUMN email;

CREATE TABLE sloth_message_fields
(
    uuid    character varying(200) NOT NULL PRIMARY KEY,
    message character varying(200) NOT NULL,
    name    character(200)         NOT NULL,
    value	text,

	CONSTRAINT message_fkey FOREIGN KEY (message)
        REFERENCES sloth_messages (uuid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);