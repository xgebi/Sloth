import psycopg
from flask import abort, redirect, request
import os
import traceback
from psycopg2 import sql
from uuid import uuid4

from app.authorization.authorize import authorize_rest, authorize_web
from app.utilities.db_connection import db_connection
from app.utilities import get_default_language, get_languages
from app.post.post_types import PostTypes
from app.toes.toes import render_toe_from_path
from app.toes.hooks import Hooks

from app.settings.localized_settings import localized_settings


@localized_settings.route("/settings/localized-settings")
@authorize_web(1)
@db_connection
def show_localized_settings(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
    """
    Shows list of localizable strings

    :param args:
    :param permission_level:
    :param connection:
    :param kwargs:
    :return:
    """
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    default_lang = get_default_language(connection=connection)
    languages = get_languages(connection=connection)
    try:
        with connection.cursor() as cur:
            cur.execute("""SELECT sls.uuid, sls.name, s.standalone, sls.content, sls.lang, sls.post_type, spt.display_name, sls2.short_name
                    FROM sloth_localized_strings AS sls 
                    INNER JOIN sloth_post_types spt on spt.uuid = sls.post_type
                    INNER JOIN sloth_localizable_strings s on s.name = sls.name
                    INNER JOIN sloth_language_settings sls2 on sls2.uuid = sls.lang;""")
            raw_post_type_strings = cur.fetchall()
            cur.execute("""SELECT sls.uuid, sls.name, s.standalone, sls.content, sls.lang, sls.post_type, sls2.short_name
                    FROM sloth_localized_strings AS sls 
                    INNER JOIN sloth_localizable_strings s on s.name = sls.name
                    INNER JOIN sloth_language_settings sls2 on sls2.uuid = sls.lang
                    WHERE s.standalone = TRUE;""", )
            raw_standalone_strings = cur.fetchall()
    except Exception as e:
        print(traceback.format_exc())
        connection.close()
        abort(500)
    connection.close()

    standalone_strings = {}
    post_type_strings = {}
    for item in raw_standalone_strings:
        if item[1] not in standalone_strings:
            standalone_strings[item[1]] = {}
        standalone_strings[item[1]][item[4]] = item[3]
    for item in raw_post_type_strings:
        if item[5] not in post_type_strings:
            post_type_strings[item[5]] = {}
        if item[1] not in post_type_strings[item[5]]:
            post_type_strings[item[5]][item[1]] = {}
        post_type_strings[item[5]][item[1]][item[4]] = item[3]
    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="localization.toe.html",
        data={
            "title": "Localization",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "default_lang": default_lang,
            "languages": languages,
            "standalone_strings": standalone_strings,
            "post_type_strings": post_type_strings
        },
        hooks=Hooks()
    )


@localized_settings.route("/settings/localized-settings/save", methods=["POST"])
@authorize_web(1)
@db_connection
def change_localized_settings(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
    """
    Saves settings for localized string

    :param args:
    :param permission_level:
    :param connection:
    :param kwargs:
    :return:
    """
    data = request.form
    languages = get_languages(connection=connection)
    try:
        cur = connection.cursor()
        cur.execute("""SELECT name, standalone FROM sloth_localizable_strings;""")

        localizable = [{"name": item[0], "standalone": item[1]} for item in cur.fetchall()]
        cur.execute("""SELECT uuid, post_type, name, lang, content FROM sloth_localized_strings;""")
        localized = {f"{item[2]}_{item[1]}_{item[3]}": {
            "uuid": item[0],
            "post_type": item[1],
            "name": item[2],
            "lang": item[3],
            "content": item[4]
        } for item in cur.fetchall()}
        to_update = []
        to_insert = []
        for item in data:
            identifiers = item.split("_")
            updated = {
                "post_type": identifiers[1] if len(identifiers) == 3 else None,
                "name": identifiers[0],
                "lang": identifiers[2] if len(identifiers) == 3 else identifiers[1],
                "content": data[item]
            }
            # 'post-type-tag-title_' + post_type['uuid'] + '_' + lang['uuid']
            if item in localized:
                updated["uuid"] = localized[item]["uuid"]
                to_update.append(updated)
                cur.execute("""UPDATE sloth_localized_strings SET content = %s WHERE uuid = %s;""",
                            (updated["content"], updated["uuid"]))
            else:
                updated["uuid"] = str(uuid4())
                to_insert.append(updated)
                cur.execute("""INSERT INTO sloth_localized_strings (uuid, post_type, name, lang, content) VALUES 
                        (%s, %s, %s, %s, %s);""",
                            (updated["uuid"], updated["post_type"], updated["name"], updated["lang"],
                             updated["content"]))
        connection.commit()
    except Exception as e:
        print(traceback.format_exc())
        connection.close()
        abort(500)
    return redirect('/settings/localized-settings')
