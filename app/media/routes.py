from flask import request, current_app, redirect, make_response
import json
from psycopg2 import sql
import uuid
from datetime import datetime
import time
import os
import traceback

from app.authorization.authorize import authorize_rest, authorize_web
from app.utilities.db_connection import db_connection_legacy
from app.utilities import get_default_language, get_languages
from app.post.post_types import PostTypes
from app.toes.hooks import Hooks
from app.toes.toes import render_toe_from_path

from app.media import media


@media.route("/media")
@authorize_web(0)
@db_connection_legacy
def show_media_list(*args, permission_level, connection, **kwargs):
    if connection is None:
        return redirect("/database-error")

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    media_data = get_media(connection=connection)
    default_lang = get_default_language(connection=connection)
    languages = get_languages(connection=connection)
    connection.close()

    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="media.toe.html",
        data={
            "title": "List of media",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "media": media_data,
            "default_lang": default_lang,
            "languages": languages,
            "json_media": json.dumps(media_data),
        },
        hooks=Hooks()
    )


@media.route("/api/media", methods=["GET"])
@authorize_rest(0)
@db_connection_legacy
def get_media_data(*args, connection, **kwargs):
    if connection is None:
        response = make_response(json.dumps({
            "error": True
        }))
        code = 500
    else:
        response = make_response(json.dumps(
            {"media": get_media(connection=connection)}
        ))
        code = 500

    response.headers['Content-Type'] = 'application/json'
    return response, code


@media.route("/api/media/upload-file", methods=['POST'])
@authorize_rest(0)
@db_connection_legacy
def upload_item(*args, connection=None, **kwargs):
    image = request.files["image"]
    alts = json.loads(request.form["alt"])
    code = -1
    try:
        cur = connection.cursor()
        cur.execute(
            sql.SQL("SELECT settings_value FROM sloth_settings WHERE settings_name = 'allowed_extensions';")
        )
        allowed_exts = cur.fetchone()[0]
        cur.close()
        ext = image.filename[image.filename.rfind(".")+1:].lower()
        mime_ext = image.mimetype[image.mimetype.rfind("/")+1:].lower()
        if not (ext in allowed_exts or mime_ext in allowed_exts):
            response = make_response(json.dumps(
                {"media": []}
            ))
            code = 500
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        response = make_response(json.dumps(
            {"media": []}
        ))
        code = 500
    now = datetime.now()
    filename = image.filename
    index = 1
    if not os.path.exists(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", str(now.year))):
        os.makedirs(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", str(now.year)))
    if not os.path.exists(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", str(now.year), str(now.month))):
        os.makedirs(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", str(now.year), str(now.month)))
    while os.path.exists(
            os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", str(now.year), str(now.month), filename)):
        if filename[:filename.rfind('.')].endswith(f"-{index - 1}"):
            filename = f"{filename[:filename.rfind('-')]}-{index}{filename[filename.rfind('.'):]}"
        else:
            filename = f"{filename[:filename.rfind('.')]}-{index}{filename[filename.rfind('.'):]}"
        index += 1

    with open(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", str(now.year), str(now.month), filename), 'wb') as f:
        image.save(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", str(now.year), str(now.month), filename))

    try:
        cur = connection.cursor()

        cur.execute(
            sql.SQL("INSERT INTO sloth_media VALUES (%s, %s, %s, %s) RETURNING uuid, file_path"),
            (str(uuid.uuid4()), os.path.join("sloth-content", str(now.year), str(now.month), filename), None,
             time.time())
        )
        file = cur.fetchone()
        connection.commit()
        for alt in alts:
            cur.execute(
                sql.SQL("INSERT INTO sloth_media_alts VALUES (%s, %s, %s, %s)"),
                (str(uuid.uuid4()), file[0], alt["lang_uuid"], alt["text"])
            )
        connection.commit()
        cur.close()
    except Exception as e:
        print(traceback.format_exc())
        response = make_response(json.dumps(
            {"media": []}
        ))
        code = 500
        connection.close()

    if code != 500:
        response = make_response(json.dumps(
            {"media": get_media(connection=connection)}
        ))
        code = 201
        connection.close()

    response.headers['Content-Type'] = 'application/json'
    return response, code


@media.route("/api/media/delete-file", methods=['POST', 'DELETE'])
@authorize_rest(0)
@db_connection_legacy
def delete_item(*args, connection=None, **kwargs):
    file_data = json.loads(request.data)

    try:
        cur = connection.cursor()
        cur.execute(
            sql.SQL("SELECT file_path FROM sloth_media WHERE uuid = %s"),
            [file_data["uuid"]]
        )
        temp_file_path = cur.fetchone()
        if len(temp_file_path) == 1:
            if os.path.exists(os.path.join(current_app.config["OUTPUT_PATH"], temp_file_path[0])):
                os.remove(os.path.join(current_app.config["OUTPUT_PATH"], temp_file_path[0]))
        else:
            response = make_response(json.dumps(
                {"media": []}
            ))
            code = 500
        cur.execute(
            sql.SQL("UPDATE sloth_posts SET thumbnail = %s WHERE thumbnail = %s;"),
            [None, file_data["uuid"]]
        )
        cur.execute(
            sql.SQL("DELETE FROM sloth_media WHERE uuid = %s"),
            [file_data["uuid"]]
        )
        connection.commit()
        cur.close()
        response = make_response(json.dumps({
            "media": get_media(connection=connection)
        }))
        code = 201
    except Exception as e:
        print(traceback.format_exc())
        connection.close()
        response = make_response(json.dumps({
            "deleted": False
        }))
        code = 500

    response.headers['Content-Type'] = 'application/json'
    return response, code


def get_media(*args, connection, **kwargs):
    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL("""SELECT settings_value FROM sloth_settings WHERE settings_name = 'site_url'""")
        )
        temp_site_url = cur.fetchone()
        if len(temp_site_url) != 1:
            return []
        site_url = temp_site_url[0]
        cur.execute(
            sql.SQL("""SELECT uuid, file_path FROM sloth_media ORDER BY added_date DESC""")
        )
        raw_media = cur.fetchall()
        media_data = {}
        for medium in raw_media:
            path_fragment = '/'.join(medium[1].split('\\'))
            media_data[medium[0]] = {
                "uuid": medium[0],
                "file_url": f"{site_url}/{path_fragment}",
                "file_path": f"{current_app.config['OUTPUT_PATH']}/{path_fragment}",
                "alts": []
            }

        cur.execute(
            sql.SQL("""SELECT sma.media, sma.lang, sma.alt, sls.long_name 
                        FROM sloth_media_alts AS sma
                        INNER JOIN sloth_language_settings as sls
                        ON sma.lang = sls.uuid;""")
        )
        raw_alts = cur.fetchall()
        for alt in raw_alts:
            if alt[0] in media_data:
                media_data[alt[0]]["alts"].append({
                    "lang_uuid": alt[1],
                    "alt": alt[2],
                    "lang": alt[3]
                })

    except Exception as e:
        print(traceback.format_exc())
        print("db error")
        return []

    cur.close()

    return media_data

