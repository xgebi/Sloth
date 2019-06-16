CREATE TABLE sloth_users (
    uuid                BIGINT  PRIMARY KEY,
    username            VARCHAR(50) UNIQUE,
    display_name        VARCHAR(100),
    password            VARCHAR(500),
    email               VARCHAR(350),
    token               VARCHAR(350),
    expiry_date         BIGINT
);