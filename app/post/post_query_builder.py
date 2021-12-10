from __future__ import annotations


def build_post_query(uuid: bool = False) -> str:
    query = """SELECT sp.uuid, sp.original_lang_entry_uuid, sp.lang, sp.slug, sp.post_type, sp.author, sp.title, 
                        sp.css, sp.use_theme_css, sp.js, sp.use_theme_js, sp.thumbnail, sp.publish_date, 
                        sp.update_date, sp.post_status, sp.imported, sp.import_approved, sp.meta_description, 
                        sp.twitter_description, spf.uuid, spf.slug, spf.display_name, sp.pinned
                        FROM sloth_posts as sp 
                        INNER JOIN sloth_post_formats spf on spf.uuid = sp.post_format"""

    if uuid:
        query = f"{query}\nWHERE sp.uuid = %s"

    return f"{query};"
