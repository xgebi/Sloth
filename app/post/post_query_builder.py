from __future__ import annotations


def build_post_query(uuid: bool = False, scheduled: bool = False, published_per_post_type: bool = False,
                     published_in_taxonomy_per_post_type: bool = False) -> str:
    query = """
SELECT sp.uuid, sp.original_lang_entry_uuid, sp.lang, sp.slug, sp.post_type, sp.author, sp.title, 
sp.css, sp.use_theme_css, sp.js, sp.use_theme_js, sp.thumbnail, sp.publish_date, 
sp.update_date, sp.post_status, sp.imported, sp.import_approved, sp.meta_description, 
sp.twitter_description, spf.uuid, spf.slug, spf.display_name, sp.pinned, su.display_name, 
su.uuid, sp.password
FROM sloth_posts as sp 
INNER JOIN sloth_users AS su ON sp.author = su.uuid
INNER JOIN sloth_post_formats spf on spf.uuid = sp.post_format""".strip()
    where = []
    order_by = []
    if uuid:
        where.append("sp.uuid = %s")
    if scheduled:
        where.append("sp.post_status = 'scheduled' AND sp.publish_date < %s")
    if published_per_post_type:
        where.append("sp.post_type = %s AND sp.lang = %s AND sp.post_status = 'published'")
        order_by.append("sp.publish_date DESC")
    if published_in_taxonomy_per_post_type:
        "\n".join([query, "INNER JOIN sloth_post_taxonomies AS spt ON sp.uuid = spt.post"])
        where.append("spt.taxonomy = %s AND sp.post_type = %s AND sp.post_status = 'published'")
        order_by.append("sp.publish_date DESC")

    if len(where) > 0:
        query = f"{query}\nWHERE {'AND'.join(where)}"
    if len(order_by) > 0:
        query = f"{query}\nORDER BY {', '.join(where)}"

    return f"{query};"
