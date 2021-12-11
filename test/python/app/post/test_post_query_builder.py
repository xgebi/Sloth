import unittest
from app.back_office.post.post_query_builder import build_post_query


class PostQueryBuilderTests(unittest.TestCase):
    def test_without_parameters(self):
        self.assertEqual(build_post_query(), """SELECT sp.uuid, sp.original_lang_entry_uuid, sp.lang, sp.slug, sp.post_type, sp.author, sp.title, 
sp.css, sp.use_theme_css, sp.js, sp.use_theme_js, sp.thumbnail, sp.publish_date, 
sp.update_date, sp.post_status, sp.imported, sp.import_approved, sp.meta_description, 
sp.twitter_description, spf.uuid, spf.slug, spf.display_name, sp.pinned, su.display_name, 
su.uuid, sp.password
FROM sloth_posts as sp 
INNER JOIN sloth_users AS su ON sp.author = su.uuid
INNER JOIN sloth_post_formats spf on spf.uuid = sp.post_format;""")

    def test_uuid(self):
        self.assertEqual(build_post_query(uuid=True), """SELECT sp.uuid, sp.original_lang_entry_uuid, sp.lang, sp.slug, sp.post_type, sp.author, sp.title, 
sp.css, sp.use_theme_css, sp.js, sp.use_theme_js, sp.thumbnail, sp.publish_date, 
sp.update_date, sp.post_status, sp.imported, sp.import_approved, sp.meta_description, 
sp.twitter_description, spf.uuid, spf.slug, spf.display_name, sp.pinned, su.display_name, 
su.uuid, sp.password
FROM sloth_posts as sp 
INNER JOIN sloth_users AS su ON sp.author = su.uuid
INNER JOIN sloth_post_formats spf on spf.uuid = sp.post_format
WHERE sp.uuid = %s;""")

    def test_scheduled(self):
        self.assertEqual(build_post_query(scheduled=True), """SELECT sp.uuid, sp.original_lang_entry_uuid, sp.lang, sp.slug, sp.post_type, sp.author, sp.title, 
sp.css, sp.use_theme_css, sp.js, sp.use_theme_js, sp.thumbnail, sp.publish_date, 
sp.update_date, sp.post_status, sp.imported, sp.import_approved, sp.meta_description, 
sp.twitter_description, spf.uuid, spf.slug, spf.display_name, sp.pinned, su.display_name, 
su.uuid, sp.password
FROM sloth_posts as sp 
INNER JOIN sloth_users AS su ON sp.author = su.uuid
INNER JOIN sloth_post_formats spf on spf.uuid = sp.post_format
WHERE sp.post_status = 'scheduled' AND sp.publish_date < %s;""")

    def test_scheduled(self):
        self.assertEqual(build_post_query(published_per_post_type=True), """SELECT sp.uuid, sp.original_lang_entry_uuid, sp.lang, sp.slug, sp.post_type, sp.author, sp.title, 
sp.css, sp.use_theme_css, sp.js, sp.use_theme_js, sp.thumbnail, sp.publish_date, 
sp.update_date, sp.post_status, sp.imported, sp.import_approved, sp.meta_description, 
sp.twitter_description, spf.uuid, spf.slug, spf.display_name, sp.pinned, su.display_name, 
su.uuid, sp.password
FROM sloth_posts as sp 
INNER JOIN sloth_users AS su ON sp.author = su.uuid
INNER JOIN sloth_post_formats spf on spf.uuid = sp.post_format
WHERE sp.post_type = %s AND sp.lang = %s AND sp.post_status = 'published'
ORDER BY sp.publish_date DESC;""")

    def test_published_in_taxonomy(self):
        self.assertEqual(build_post_query(published_in_taxonomy_per_post_type=True), """SELECT sp.uuid, sp.original_lang_entry_uuid, sp.lang, sp.slug, sp.post_type, sp.author, sp.title, 
sp.css, sp.use_theme_css, sp.js, sp.use_theme_js, sp.thumbnail, sp.publish_date, 
sp.update_date, sp.post_status, sp.imported, sp.import_approved, sp.meta_description, 
sp.twitter_description, spf.uuid, spf.slug, spf.display_name, sp.pinned, su.display_name, 
su.uuid, sp.password
FROM sloth_posts as sp 
INNER JOIN sloth_users AS su ON sp.author = su.uuid
INNER JOIN sloth_post_formats spf on spf.uuid = sp.post_format
INNER JOIN sloth_post_taxonomies AS spt ON sp.uuid = spt.post
WHERE spt.taxonomy = %s AND sp.post_type = %s AND sp.post_status = 'published'
ORDER BY sp.publish_date DESC;""")

    def test_uuid_scheduled(self):
        self.assertEqual(build_post_query(uuid=True, scheduled=True), """SELECT sp.uuid, sp.original_lang_entry_uuid, sp.lang, sp.slug, sp.post_type, sp.author, sp.title, 
sp.css, sp.use_theme_css, sp.js, sp.use_theme_js, sp.thumbnail, sp.publish_date, 
sp.update_date, sp.post_status, sp.imported, sp.import_approved, sp.meta_description, 
sp.twitter_description, spf.uuid, spf.slug, spf.display_name, sp.pinned, su.display_name, 
su.uuid, sp.password
FROM sloth_posts as sp 
INNER JOIN sloth_users AS su ON sp.author = su.uuid
INNER JOIN sloth_post_formats spf on spf.uuid = sp.post_format
WHERE sp.uuid = %s AND sp.post_status = 'scheduled' AND sp.publish_date < %s;""")

    def test_original_and_other_languages(self):
        try:
            build_post_query(original_other_language_versions=True, other_language_versions_only=True)
        except Exception as e:
            self.assertEqual(type(e), Exception)
            return
        self.assertEqual(False, True)

    def test_original_other_language_version(self):
        self.assertEqual(build_post_query(original_other_language_versions=True), """SELECT sp.uuid, sp.original_lang_entry_uuid, sp.lang, sp.slug, sp.post_type, sp.author, sp.title, 
sp.css, sp.use_theme_css, sp.js, sp.use_theme_js, sp.thumbnail, sp.publish_date, 
sp.update_date, sp.post_status, sp.imported, sp.import_approved, sp.meta_description, 
sp.twitter_description, spf.uuid, spf.slug, spf.display_name, sp.pinned, su.display_name, 
su.uuid, sp.password
FROM sloth_posts as sp 
INNER JOIN sloth_users AS su ON sp.author = su.uuid
INNER JOIN sloth_post_formats spf on spf.uuid = sp.post_format
WHERE sp.original_lang_entry_uuid = %s;""")

    def test_uuid_scheduled(self):
        self.assertEqual(build_post_query(other_language_versions_only=True), """SELECT sp.uuid, sp.original_lang_entry_uuid, sp.lang, sp.slug, sp.post_type, sp.author, sp.title, 
sp.css, sp.use_theme_css, sp.js, sp.use_theme_js, sp.thumbnail, sp.publish_date, 
sp.update_date, sp.post_status, sp.imported, sp.import_approved, sp.meta_description, 
sp.twitter_description, spf.uuid, spf.slug, spf.display_name, sp.pinned, su.display_name, 
su.uuid, sp.password
FROM sloth_posts as sp 
INNER JOIN sloth_users AS su ON sp.author = su.uuid
INNER JOIN sloth_post_formats spf on spf.uuid = sp.post_format
WHERE sp.uuid = %s OR (sp.original_lang_entry_uuid = %s AND sp.uuid <> %s);""")


if __name__ == '__main__':
    unittest.main()
