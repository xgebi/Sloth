SELECT sp.uuid, sp.original_lang_entry_uuid, sp.lang, sp.slug, sp.post_type, sp.author, sp.title,
sp.css, sp.use_theme_css, sp.js, sp.use_theme_js, sp.thumbnail, sp.publish_date,
sp.update_date, sp.post_status, sp.imported, sp.import_approved, sp.meta_description,
sp.twitter_description, spf.uuid as post_format_uuid, spf.slug  as post_format_slug,
spf.display_name as post_format_name, sp.pinned, su.display_name as author_name, sp.password
FROM sloth_posts as sp
INNER JOIN sloth_users AS su ON sp.author = su.uuid
INNER JOIN sloth_post_formats spf on spf.uuid = sp.post_format