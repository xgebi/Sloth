CREATE TYPE sloth_message_type AS ENUM ('read', 'unread', 'deleted');

CREATE TABLE sloth_messages (
	uuid character varying(200) NOT NULL PRIMARY KEY,
	name character(200) NOT NULL,
	email character(350) NOT NULL,
	body text NOT NULL,
	sent_date double precision,
	status sloth_message_type
);