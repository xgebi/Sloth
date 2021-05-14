CREATE TABLE sloth_libraries (
    uuid varchar(200) NOT NULL,
    name text,
    version text,
    location text UNIQUE,

    PRIMARY KEY (uuid)
)