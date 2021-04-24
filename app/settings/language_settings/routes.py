from flask import request, flash, url_for, current_app, abort, render_template
import app
import os
from pathlib import Path
import psycopg2
from psycopg2 import sql
import bcrypt
import json
import uuid
from app.post.post_types import PostTypes
from app.authorization.authorize import authorize_rest, authorize_web
from app.utilities import get_default_language
from app.utilities.db_connection import db_connection

from app.settings.language_settings import language_settings


@language_settings.route("/settings/language", methods=["GET"])
@authorize_web(1)
@db_connection
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
    # Languages
    return render_template("language.toe.html", post_types=post_types_result, permission_level=permission_level,
                           languages=languages, default_lang=default_lang)


@language_settings.route("/api/settings/language/<lang_id>/save", methods=["POST", "PUT"])
@authorize_rest(1)
@db_connection
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

    return json.dumps(result)


@language_settings.route("/api/settings/language/<lang_id>/delete", methods=["DELETE"])
@authorize_rest(1)
@db_connection
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
    except Exception as e:
        print(e)
        abort(500)

    cur.close()
    connection.close()

    return json.dumps({
        "uuid": lang_id,
        "deleted": True
    })
