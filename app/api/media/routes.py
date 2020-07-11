from flask import request, flash, url_for, current_app, abort
import json
import psycopg2
from psycopg2 import sql, errors
import uuid
from time import time
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
    file_data = json.loads(request.data)
    request.files["iwage"] # filename stream mimetype
    request.form["alt"]
    ext = file_name[file_name.rfind("."):]
    if not ext.lower() in (".png", ".jpg", ".jpeg", ".svg", ".bmp", ".tiff"): # TODO do this in config
        abort(500)
    with open(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", file_name), 'wb') as f:
        f.write(request.data)

    file = {}

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

