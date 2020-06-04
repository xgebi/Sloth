-- Post types
INSERT INTO sloth_post_types VALUES ('1adbec5d-f4a1-401d-9274-3552f1219f36', 'post', 'Post', true, true, true );
INSERT INTO sloth_post_types VALUES ('f00b6733-d38b-489d-90cc-76e7c4dc1651', 'page', 'Page', true, true, false );

-- Sample post
INSERT INTO sloth_posts VALUES ('76c05278-749d-47fe-b782-a4ecd5d27cb6', '', '', 'en', 'first-post', '1adbec5d-f4a1-401d-9274-3552f1219f36', null, 'First post', '<p>Hello! This is the first post.</p>', '', '', '', NULL, 1562420418000, 1562420418000, 'published', '{}', '{}', false);
UPDATE sloth_posts SET author = (SELECT uuid FROM sloth_users LIMIT 1);

-- Initial Settings
INSERT INTO sloth_settings VALUES('active_theme', '', 'text', 'themes', 'white');
commit;