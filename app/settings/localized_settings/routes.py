from flask import abort, redirect, request
import os
import traceback
from psycopg2 import sql

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
def show_localized_settings(*args, permission_level, connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    default_lang = get_default_language(connection=connection)
    languages = get_languages(connection=connection)
    try:
        cur = connection.cursor()
        cur.execute(
            sql.SQL(
                """SELECT sls.uuid, sls.name, s.standalone, sls.content, sls.lang, sls.post_type, spt.display_name, sls2.short_name
                FROM sloth_localized_strings AS sls 
                INNER JOIN sloth_post_types spt on spt.uuid = sls.post_type
                INNER JOIN sloth_localizable_strings s on s.name = sls.name
                INNER JOIN sloth_language_settings sls2 on sls2.uuid = sls.lang;"""),
        )
        localized_strings = cur.fetchall()
    except Exception as e:
        print(traceback.format_exc())
        connection.close()
        abort(500)

    standalone_strings = {}
    post_type_strings = {}
    for item in localized_strings:
        if item[2]:
            if item[1] not in standalone_strings:
                standalone_strings[item[1]] = {}
            standalone_strings[item[1]][item[7]] = item[3]
        else:
            if item[5] not in post_type_strings:
                post_type_strings[item[5]] = {}
            if item[1] not in post_type_strings:
                post_type_strings[item[1]] = {}
            post_type_strings[item[5]][item[1]][item[7]] = item[3]

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
def change_localized_settings(*args, permission_level, connection, **kwargs):
    data = request.form
    # for item in data:
    #     print(f"{item}: {data[item]}")
    try:
        cur = connection.cursor()
        cur.execute(
            sql.SQL(
                """SELECT uuid, post_type, name, lang, content FROM sloth_localized_strings;"""),
        )

        cur.execute(
            sql.SQL(
                """INSERT INTO sloth_localized_strings (uuid, name, content, lang, post_type)
                        VALUES ('sitename', TRUE)
                        ON CONFLICT (name) 
                        DO 
                           UPDATE SET standalone = TRUE WHERE sloth_localizable_strings.name = 'sitename';"""),
            (, )
        )
    except Exception as e:
        print(traceback.format_exc())
        connection.close()
        abort(500)
    return redirect('/settings/localized-settings')
