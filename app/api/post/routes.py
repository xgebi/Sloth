from flask import request, flash, url_for, current_app, abort
import json
import psycopg2
from psycopg2 import sql, errors
import uuid
from time import time
import os
import traceback

from app.utilities.db_connection import db_connection
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize_rest
from app.utilities.db_connection import db_connection
from app.posts.posts_generator import PostsGenerator

from app.api.post import post

reserved_folder_names = ('tag', 'category')


@post.route("/api/post/media", methods=["GET"])
@authorize_rest(0)
@db_connection
def get_media_data(*args, connection, **kwargs):
    if connection is None:
        abort(500)

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

    media = []
    for medium in raw_media:
        media.append({
            "uuid": medium[0],
            "filePath": medium[1],
            "alt": medium[2]
        })

    return json.dumps({"media": media})


@post.route("/api/post/upload-file", methods=['POST'])
@authorize_rest(0)
@db_connection
def upload_image(*args, file_name, connection=None, **kwargs):
    ext = file_name[file_name.rfind("."):]
    if not ext.lower() in (".png", ".jpg", ".jpeg", ".svg", ".bmp", ".tiff"):
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

    return json.dumps({ "media": file }), 201