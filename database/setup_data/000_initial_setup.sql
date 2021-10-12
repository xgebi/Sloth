-- Post types and formats
INSERT INTO sloth_post_types VALUES ('1adbec5d-f4a1-401d-9274-3552f1219f36', 'post', 'Post', true, true, true );
INSERT INTO sloth_post_formats (uuid, slug, display_name, post_type, deletable)
VALUES ('30c0b63f-abd8-4b73-8fe0-2a6154671300', 'none', 'None',
        '1adbec5d-f4a1-401d-9274-3552f1219f36', FALSE);
INSERT INTO sloth_post_types
VALUES ('f00b6733-d38b-489d-90cc-76e7c4dc1651', 'page', 'Page', true, true, false);
INSERT INTO sloth_post_formats (uuid, slug, display_name, post_type, deletable)
VALUES ('1a91d5c4-ec37-4988-a657-27e058acc7e4', 'none', 'None',
        'f00b6733-d38b-489d-90cc-76e7c4dc1651', FALSE);

-- Sample post
INSERT INTO sloth_posts (uuid, original_lang_entry_uuid, lang, slug, post_type, author, title, content, excerpt, css,
                         js, thumbnail, publish_date, update_date, post_status, post_format, password,
                         meta_description, twitter_description)
VALUES ('76c05278-749d-47fe-b782-a4ecd5d27cb6', NULL,
        (SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language'), 'first-post',
        '1adbec5d-f4a1-401d-9274-3552f1219f36', (SELECT uuid FROM sloth_users LIMIT 1),
        'First post', '', '', '', '', NULL, (SELECT extract(epoch from current_timestamp) * 1000),
        (SELECT extract(epoch from current_timestamp) * 1000), 'published',
        (SELECT uuid FROM sloth_post_formats WHERE post_type = '1adbec5d-f4a1-401d-9274-3552f1219f36' AND slug = 'none'),
        '', '', '');
INSERT INTO sloth_post_sections (uuid, post, content, section_type, position)
VALUES ('fd971946-3843-433e-91dc-7e108f7065c2', '76c05278-749d-47fe-b782-a4ecd5d27cb6', 'This is a first post', 'text', 0);

-- Initial Settings
INSERT INTO sloth_settings VALUES('active_theme', '', 'text', 'themes', 'light');
INSERT INTO sloth_settings VALUES('wordpress_import_count', '', 'text', 'import', '0');
INSERT INTO sloth_settings VALUES('allowed_extensions', 'Allowed extensions', 'text', 'sloth', 'png, jpg, jpeg, svg, bmp, tiff, js, css, zip, tar');
commit;