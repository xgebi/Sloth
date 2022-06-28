import psycopg
from typing import Dict, Any
import datetime
import sys

from app.utilities.utility_exceptions import NoPositiveMinimumException
from app.back_office.post.post_query_builder import build_post_query, normalize_post_from_query


def get_languages(*args, connection: psycopg.Connection, lang_id: str = "", as_list: bool = True, **kwargs):
    try:
        with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute("""SELECT uuid, long_name, short_name FROM sloth_language_settings""")
            temp_languages = cur.fetchall()
    except Exception as e:
        print(e)
        return ()

    if len(lang_id) != 0:
        languages = [lang for lang in temp_languages if lang[0] != lang_id]
        current_lang = [lang for lang in temp_languages if lang[0] == lang_id][0]

        return current_lang, languages
    if as_list:
        return temp_languages
    return {lang['uuid']: lang for lang in temp_languages}


def get_default_language(*args, connection: psycopg.Connection, **kwargs) -> Dict[str, str]:
    with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
        try:
            cur.execute(
                """SELECT uuid, long_name FROM sloth_language_settings 
                WHERE uuid = (SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language')"""
            )
            main_language = cur.fetchone()
        except psycopg.errors.DatabaseError as e:
            print(e)
            return {}

        return main_language


def get_related_posts(*args, post, connection, **kwargs):
    cur = connection.cursor(row_factory=psycopg.rows.dict_row)
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
    related_posts = [normalize_post_from_query(post) for post in cur.fetchall()]

    for related_post in related_posts:
        cur.execute(
            """SELECT content, section_type, position
                FROM sloth_post_sections
                WHERE post = %s
                ORDER BY position;""",
            (related_post["uuid"],)
        )
        sections = [{
            "content": section[0],
            "type": section[1],
            "position": section[2]
        } for section in cur.fetchall()]
        related_post.update({
            "meta_description": prepare_description(char_limit=161, description=post["meta_description"], section=sections[0]),
            "twitter_description": prepare_description(char_limit=161, description=post["twitter_description"], section=sections[0]),
            "sections": sections,
        })

    for post in related_posts:
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
    return related_posts


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
