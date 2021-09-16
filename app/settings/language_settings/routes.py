from flask import request, abort, make_response
from psycopg2 import sql
import json
import uuid
import os
from app.post.post_types import PostTypes
from app.authorization.authorize import authorize_rest, authorize_web
from app.utilities import get_default_language
from app.utilities.db_connection import db_connection_legacy
from app.toes.toes import render_toe_from_path
from app.toes.hooks import Hooks

from app.settings.language_settings import language_settings


@language_settings.route("/settings/language", methods=["GET"])
@authorize_web(1)
@db_connection_legacy
def show_language_settings(*args, permission_level, connection=None, **kwargs):
    if connection is None:
        abort(500)

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    cur = connection.cursor()
    temp_languages = []
    default_language = ""
    try:
        cur.execute(
            sql.SQL("""SELECT settings_value from sloth_settings WHERE settings_name = %s"""),
            ['main_language']
        )
        default_language = cur.fetchone()[0]
        cur.execute(
            sql.SQL("""SELECT uuid, short_name, long_name FROM sloth_language_settings""")
        )
        temp_languages = cur.fetchall()
    except Exception as e:
        print(e)
        abort(500)
    cur.close()
    default_lang = get_default_language(connection=connection)
    connection.close()

    languages = []
    for lang in temp_languages:
        languages.append({
            "uuid": lang[0],
            "short_name": lang[1],
            "long_name": lang[2],
            "default": lang[0] == default_language
        })

    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="language.toe.html",
        data={
            "title": "Languages",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "default_lang": default_lang,
            "languages": languages
        },
        hooks=Hooks()
    )


@language_settings.route("/api/settings/language/<lang_id>/save", methods=["POST", "PUT"])
@authorize_rest(1)
@db_connection_legacy
def save_language_info(*args, connection=None, lang_id: str, **kwargs):
    if connection is None:
        abort(500)

    filled = json.loads(request.data)

    cur = connection.cursor()
    try:
        if lang_id.startswith("new-"):
            cur.execute(
                sql.SQL("""INSERT INTO sloth_language_settings VALUES (%s, %s, %s)
                RETURNING uuid, short_name, long_name;"""),
                [str(uuid.uuid4()), filled["shortName"], filled["longName"]]
            )
        else:
            cur.execute(
                sql.SQL("""UPDATE sloth_language_settings SET short_name = %s, long_name = %s WHERE uuid = %s
                RETURNING uuid, short_name, long_name;"""),
                [filled["shortName"], filled["longName"], lang_id]
            )
        connection.commit()
        temp_result = cur.fetchone()
    except Exception as e:
        print(e)
        abort(500)

    cur.close()
    connection.close()

    result = {
        "uuid": temp_result[0],
        "shortName": temp_result[1],
        "longName": temp_result[2]
    }
    if lang_id.startswith("new-"):
        result["new"] = True
        result["oldUuid"] = lang_id

    response = make_response(json.dumps(result))
    response.headers['Content-Type'] = 'application/json'
    code = 200

    return response, code


@language_settings.route("/api/settings/language/<lang_id>/delete", methods=["DELETE"])
@authorize_rest(1)
@db_connection_legacy
def delete_language(*args, connection=None, lang_id: str, **kwargs):
    if connection is None:
        abort(500)

    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL("""DELETE FROM sloth_language_settings WHERE uuid = %s;"""),
            [lang_id]
        )
        connection.commit()
        cur.close()
        connection.close()

        response = make_response(json.dumps({
            "uuid": lang_id,
            "deleted": True
        }))
        code = 200
    except Exception as e:
        print(e)
        response = make_response(json.dumps({
            "uuid": lang_id,
            "deleted": False
        }))
        code = 200

    response.headers['Content-Type'] = 'application/json'
    return response, code
