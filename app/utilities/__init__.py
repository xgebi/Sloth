from psycopg2 import sql
from typing import Tuple, List, Dict, Any
import datetime
import sys

from app.utilities.utility_exceptions import NoPositiveMinimumException


def get_languages(*args, connection, lang_id: str = "", **kwargs) \
        -> Tuple[Dict[str, Any], List[Dict[str, Any]]] or List[Dict[str, Any]]:
    cur = connection.cursor()
    temp_languages = []
    try:
        cur.execute(
            sql.SQL("""SELECT uuid, long_name, short_name FROM sloth_language_settings""")
        )
        temp_languages = cur.fetchall()
    except Exception as e:
        print(e)
        return ()

    if len(lang_id) != 0:
        languages = [{
            "uuid": lang[0],
            "long_name": lang[1],
            "short_name": lang[2]
        } for lang in temp_languages if lang[0] != lang_id]
        current_lang = [{
            "uuid": lang[0],
            "long_name": lang[1],
            "short_name": lang[2]
        } for lang in temp_languages if lang[0] == lang_id][0]

        return current_lang, languages
    return [{
        "uuid": lang[0],
        "long_name": lang[1],
        "short_name": lang[2]
    } for lang in temp_languages]


def get_default_language(*args, connection, **kwargs) -> Dict[str, str]:
    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL("""SELECT uuid, long_name FROM sloth_language_settings 
            WHERE uuid = (SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language')""")
        )
        main_language = cur.fetchone()
    except Exception as e:
        print(e)
        return {}

    return {
        "uuid": main_language[0],
        "long_name": main_language[1]
    }


def get_related_posts(*args, post, connection, **kwargs):
    cur = connection.cursor()
    if post["original_lang_entry_uuid"] is not None and len(post["original_lang_entry_uuid"]) > 0:
        cur.execute(
            sql.SQL(
                """SELECT A.uuid, A.original_lang_entry_uuid, A.lang, A.slug, A.post_type, A.author, A.title,
                 A.content, A.excerpt, A.css, A.use_theme_css, A.js, A.use_theme_js, A.thumbnail, A.publish_date, 
                 A.update_date, A.post_status, A.imported, A.import_approved FROM sloth_posts as A 
                 WHERE A.uuid = %s OR (A.original_lang_entry_uuid = %s AND A.uuid <> %s);"""),
            (post["original_lang_entry_uuid"], post["original_lang_entry_uuid"],
             post["uuid"])
        )
    else:
        cur.execute(
            sql.SQL(
                """SELECT A.uuid, A.original_lang_entry_uuid, A.lang, A.slug, A.post_type, A.author, A.title, 
                A.content, A.excerpt, A.css, A.use_theme_css, A.js, A.use_theme_js, A.thumbnail, A.publish_date, 
                A.update_date, A.post_status, A.imported, A.import_approved FROM sloth_posts as A 
                WHERE A.original_lang_entry_uuid = %s;"""),
            (post["uuid"],)
        )
    related_posts_raw = cur.fetchall()
    cur.close()
    return [parse_raw_post(related_post) for related_post in related_posts_raw]


def parse_raw_post(raw_post) -> Dict[str, str] or Any:
    result = {
        "uuid": raw_post[0],
        "original_lang_entry_uuid": raw_post[1],
        "lang": raw_post[2],
        "slug": raw_post[3],
        "post_type": raw_post[4],
        "author": raw_post[5],
        "title": raw_post[6],
        "content": raw_post[7],
        "excerpt": raw_post[8],
        "css": raw_post[9],
        "use_theme_css": raw_post[10],
        "js": raw_post[11],
        "use_theme_js": raw_post[12],
        "thumbnail": raw_post[13],
        "publish_date": raw_post[14],
        "publish_date_formatted": datetime.datetime.fromtimestamp(float(raw_post[14]) / 1000).strftime(
            "%Y-%m-%d %H:%M") if raw_post[14] is not None else None,
        "update_date": raw_post[15],
        "update_date_formatted": datetime.datetime.fromtimestamp(float(raw_post[15]) / 1000).strftime(
            "%Y-%m-%d %H:%M") if raw_post[15] is not None else None,
        "post_status": raw_post[16],
        "imported": raw_post[17],
        "approved": raw_post[18],
        "meta_description": raw_post[19] if len(raw_post) >= 20 and raw_post[19] is not None and len(raw_post[19]) > 0 else raw_post[8][:161 if len(raw_post[8]) > 161 else len(raw_post[8])],
        "social_description": raw_post[20] if len(raw_post) >= 21 and raw_post[20] is not None and len(raw_post[20]) > 0 else raw_post[8][:201 if len(raw_post[8]) > 201 else len(raw_post[8])],
        "format_uuid": raw_post[21] if len(raw_post) >= 22 and raw_post[21] is not None else None,
        "format_slug": raw_post[22] if len(raw_post) >= 23 and raw_post[22] is not None else None,
        "format_name": raw_post[23] if len(raw_post) >= 24 and raw_post[23] is not None else None,
    }

    return result


def positive_min(*args, floats: bool = False):
    if floats:
        args = [float(arg) for arg in args if arg >= 0]
    else:
        args = [int(arg) for arg in args if arg >= 0]
    positive_minimum = sys.maxsize
    pm_change = False
    for arg in args:
        if arg < positive_minimum:
            pm_change = True
            positive_minimum = arg
    if not pm_change:
        raise NoPositiveMinimumException()
    return positive_minimum
