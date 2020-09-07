CREATE TABLE sloth_mock_endpoints (
    uuid character varying(200),
    path text NOT NULL,
    data text NOT NULL,

    PRIMARY KEY(uuid)
)