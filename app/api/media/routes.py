from flask import request, flash, url_for, current_app, abort
import json
import psycopg2
from psycopg2 import sql, errors
import uuid
from datetime import datetime
import os
import traceback

from app.authorization.authorize import authorize_rest
from app.utilities.db_connection import db_connection

from app.api.media import media


@media.route("/api/media", methods=["GET"])
@authorize_rest(0)
@db_connection
def get_media_data(*args, connection, **kwargs):
    if connection is None:
        abort(500)

    return json.dumps({"media": get_media(connection=connection)})


@media.route("/api/media/upload-file", methods=['POST'])
@authorize_rest(0)
@db_connection
def upload_item(*args, connection=None, **kwargs):
    image = request.files["image"] # filename stream mimetype
    alt = request.form["alt"]

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
            abort(500)
    except Exception as e:
        print(e)
        abort(500)
    now = datetime.now()
    filename = image.filename
    index = 1
    while os.path.exists(
            os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", str(now.year), str(now.month), filename)):
        if filename[:filename.rfind('.')].endswith(f"-{index - 1}"):
            filename = f"{filename[:filename.rfind('-')]}-{index}{filename[filename.rfind('.'):]}"
        else:
            filename = f"{filename[:filename.rfind('.')]}-{index}{filename[filename.rfind('.'):]}"
        index += 1

    with open(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", str(now.year), str(now.month), filename), 'wb') as f:
        image.save(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", str(now.year), str(now.month), filename))

    file = {}

    try:
        cur = connection.cursor()

        cur.execute(
            sql.SQL("INSERT INTO sloth_media VALUES (%s, %s, %s, %s) RETURNING uuid, file_path, alt"),
            [str(uuid.uuid4()), os.path.join("sloth-content", str(now.year), str(now.month), filename), alt, None]
        )
        file = cur.fetchone()
        cur.close()
    except Exception as e:
        print(traceback.format_exc())
        connection.close()
        abort(500)
    connection.close()
    return json.dumps({"media": file}), 201


@media.route("/api/media/delete-file", methods=['POST', 'DELETE'])
@authorize_rest(0)
@db_connection
def delete_item(*args, connection=None, **kwargs):
    file_data = json.loads(request.data)

    try:
        cur = connection.cursor()

        cur.execute(
            sql.SQL("INSERT INTO settings_media VALUES (%s, %s, %s, %s) RETURNING uuid, file_path, alt"),
            [str(uuid.uuid4()), os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", file_name), "", ""]
        )
        file = cur.fetchone()
        cur.close()
    except Exception as e:
        print(traceback.format_exc())
        connection.close()
        abort(500)

    return json.dumps({ "media": file }), 201


def get_media(*args, connection, **kwargs):
    cur = connection.cursor()
    raw_media = []
    try:

        cur.execute(
            sql.SQL("SELECT uuid, file_path, alt FROM sloth_media")
        )
        raw_media = cur.fetchall()
    except Exception as e:
        print("db error")
        abort(500)

    cur.close()
    connection.close()

    media_data = []
    for medium in raw_media:
        media_data.append({
            "uuid": medium[0],
            "filePath": medium[1],
            "alt": medium[2]
        })
    return media_data

