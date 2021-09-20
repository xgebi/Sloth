CREATE TABLE sloth_ban_list (
    uuid character varying(200) NOT NULL PRIMARY KEY,
    ip text,
    attempts int,
    last_attempt double precision,
    banned_until double precision,
    time_period double precision
)