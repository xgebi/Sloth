from __future__ import annotations

import datetime
from typing import List, Dict


def build_post_query(uuid: bool = False, scheduled: bool = False, published_per_post_type: bool = False,
                     published_in_taxonomy_per_post_type: bool = False, original_other_language_versions: bool = False,
                     other_language_versions_only: bool = False) -> str:
    query = """
SELECT sp.uuid, sp.original_lang_entry_uuid, sp.lang, sp.slug, sp.post_type, sp.author, sp.title, 
sp.css, sp.use_theme_css, sp.js, sp.use_theme_js, sp.thumbnail, sp.publish_date, 
sp.update_date, sp.post_status, sp.imported, sp.import_approved, sp.meta_description, 
sp.twitter_description, spf.uuid, spf.slug, spf.display_name, sp.pinned, su.display_name, sp.password
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
        query = "\n".join([query, "INNER JOIN sloth_post_taxonomies AS spt ON sp.uuid = spt.post"])
        where.append("spt.taxonomy = %s AND sp.post_type = %s AND sp.post_status = 'published'")
        order_by.append("sp.publish_date DESC")

    if original_other_language_versions and other_language_versions_only:
        raise Exception("original_other_language_versions and other_language_versions_only can't be both true")

    if original_other_language_versions and not other_language_versions_only:
        where.append("sp.original_lang_entry_uuid = %s")

    if other_language_versions_only and not original_other_language_versions:
        where.append("sp.uuid = %s OR (sp.original_lang_entry_uuid = %s AND sp.uuid <> %s)")

    if len(where) > 0:
        query = f"{query}\nWHERE {' AND '.join(where)}"
    if len(order_by) > 0:
        query = f"{query}\nORDER BY {', '.join(order_by)}"

    return f"{query};"


def normalize_post_from_query(post: List) -> Dict | None:
    if len(post) == 0:
        return None
    return {
        "uuid": post[0],
        "original_lang_entry_uuid": post[1],
        "lang": post[2],
        "slug": post[3],
        "post_type": post[4],
        "author": post[5],
        "title": post[6],
        "css": post[7],
        "use_theme_css": post[8],
        "js": post[9],
        "use_theme_js": post[10],
        "thumbnail": post[11],
        "publish_date": post[12],
        "publish_timedate_formatted": datetime.datetime.fromtimestamp(float(post[12]) / 1000).strftime(
            "%Y-%m-%d %H:%M") if post[12] is not None else None,
        "publish_date_formatted": datetime.datetime.fromtimestamp(float(post[12]) / 1000).strftime("%Y-%m-%d") if post[12] else None,
        "publish_time_formatted": datetime.datetime.fromtimestamp(float(post[12]) / 1000).strftime("%H:%M") if post[12] else None,
        "update_date": post[13],
        "update_date_formatted": datetime.datetime.fromtimestamp(float(post[13]) / 1000).strftime(
            "%Y-%m-%d %H:%M") if post[13] is not None else None,
        "status": post[14],
        "imported": post[15],
        "import_approved": post[16],
        "meta_description": post[17],
        "twitter_description": post[18],
        "post_format_uuid": post[19],
        "post_format_slug": post[20],
        "post_format_name": post[21],
        "pinned": post[22],
        "author_name": post[23],
        "password": post[24]
    }
