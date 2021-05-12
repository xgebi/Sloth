from flask import abort
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
                """SELECT name FROM sloth_localizable_strings;"""),
        )
        localizable_strings = cur.fetchall()
        cur.execute(
            sql.SQL(
                """SELECT sls.uuid, sls.name, sls.content, sls.lang, sls.post_type, spt.display_name
                FROM sloth_localized_strings AS sls 
                INNER JOIN sloth_post_types spt on spt.uuid = sls.post_type;"""),
        )
        localized_strings = cur.fetchall()
    except Exception as e:
        print(traceback.format_exc())
        connection.close()
        abort(500)

    temp_items = {name[0]: {} for name in localizable_strings}
    for string in localized_strings:
        pass

    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="localization.toe.html",
        data={
            "title": "Localization",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "default_lang": default_lang,
            "languages": languages
        },
        hooks=Hooks()
    )


@localized_settings.route("/settings/localized-settings/save", methods=["POST"])
@authorize_web(1)
@db_connection
def change_localized_settings(*args, permission_level, connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    default_lang = get_default_language(connection=connection)
    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="localized-settings.toe.html",
        data={
            "title": "Dashboard",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "default_lang": default_lang
        },
        hooks=Hooks()
    )
