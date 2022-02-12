import psycopg
from typing import Dict, Any
import datetime
import sys

from app.utilities.utility_exceptions import NoPositiveMinimumException
from app.back_office.post.post_query_builder import build_post_query, normalize_post_from_query


def get_languages(*args, connection: psycopg.Connection, lang_id: str = "", as_list: bool = True, **kwargs):
    try:
        with connection.cursor() as cur:
            cur.execute("""SELECT uuid, long_name, short_name FROM sloth_language_settings""")
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
    if as_list:
        return [{
            "uuid": lang[0],
            "long_name": lang[1],
            "short_name": lang[2]
        } for lang in temp_languages]
    return {lang[0]: {
        "uuid": lang[0],
        "long_name": lang[1],
        "short_name": lang[2]
    } for lang in temp_languages}


def get_default_language(*args, connection: psycopg.Connection, **kwargs) -> Dict[str, str]:
    with connection.cursor() as cur:
        try:
            cur.execute(
                """SELECT uuid, long_name FROM sloth_language_settings 
                WHERE uuid = (SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language')"""
            )
            main_language = cur.fetchone()
        except psycopg.errors.DatabaseError as e:
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
            build_post_query(other_language_versions_only=True),
            (post["original_lang_entry_uuid"], post["original_lang_entry_uuid"], post["uuid"])
        )
    else:
        cur.execute(
            build_post_query(original_other_language_versions=True),
            (post["uuid"],)
        )
    related_posts_raw = [normalize_post_from_query(post) for post in cur.fetchall()]

    posts = []
    for related_post in related_posts_raw:
        cur.execute(
            """SELECT content, section_type, position
                FROM sloth_post_sections
                WHERE post = %s
                ORDER BY position;""",
            (related_post[0],)
        )
        sections = [{
            "content": section[0],
            "type": section[1],
            "position": section[2]
        } for section in cur.fetchall()]
        parse_raw_post(related_post, sections=sections)

    for post in posts:
        cur.execute(
            """SELECT sl.location, spl.hook_name
                FROM sloth_post_libraries AS spl
                INNER JOIN sloth_libraries sl on sl.uuid = spl.library
                WHERE spl.post = %s;""",
            (post["uuid"],)
        )
        post["libraries"] = [{
            "location": lib[0],
            "hook_name": lib[1]
        } for lib in cur.fetchall()]
    cur.close()
    return posts


def parse_raw_post(raw_post, sections) -> Dict[str, str] or Any:
    return {
        "uuid": raw_post[0],
        "original_lang_entry_uuid": raw_post[1],
        "lang": raw_post[2],
        "slug": raw_post[3],
        "post_type": raw_post[4],
        "author": raw_post[5],
        "title": raw_post[6],
        "css": raw_post[7],
        "use_theme_css": raw_post[8],
        "js": raw_post[9],
        "use_theme_js": raw_post[10],
        "thumbnail": raw_post[11],
        "publish_date": raw_post[12],
        "publish_date_formatted": datetime.datetime.fromtimestamp(float(raw_post[12]) / 1000).strftime(
            "%Y-%m-%d %H:%M") if raw_post[12] is not None else None,
        "update_date": raw_post[13],
        "update_date_formatted": datetime.datetime.fromtimestamp(float(raw_post[13]) / 1000).strftime(
            "%Y-%m-%d %H:%M") if raw_post[13] is not None else None,
        "post_status": raw_post[14],
        "imported": raw_post[15],
        "approved": raw_post[16],
        "meta_description": prepare_description(char_limit=161, description=raw_post[17], section=sections[0]),
        "social_description": prepare_description(char_limit=161, description=raw_post[18], section=sections[0]),
        "format_uuid": raw_post[19],
        "format_slug": raw_post[20],
        "format_name": raw_post[21],
        "sections": sections,
        "pinned": raw_post[22],
        "author_display_name": raw_post[23],
        "password": raw_post[24],
    }


def prepare_description(char_limit: int, description: str, section: Dict) -> str:
    if description is not None and len(description) > 0:
        return description
    if len(section["content"]) > char_limit:
        return section["content"][:char_limit]
    return section["content"]


def positive_min(*args, floats: bool = False) -> int or float:
    """
    Calculates positive minimum

    :param args:
    :param floats:
    :return:
    """
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


def get_connection_dict(config) -> Dict:
    """
    Creates a dict with connection information

    :param config:
    :return:
    """
    return {
        "dbname": config["DATABASE_NAME"],
        "user": config["DATABASE_USER"],
        "host": config["DATABASE_URL"],
        "port": str(config["DATABASE_PORT"]),
        "password": config["DATABASE_PASSWORD"],
    }
