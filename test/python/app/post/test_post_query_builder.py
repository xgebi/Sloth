import unittest
from app.post.post_query_builder import build_post_query


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

if __name__ == '__main__':
    unittest.main()
