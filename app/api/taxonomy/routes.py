from flask import request, flash, url_for, current_app, abort
import json
import psycopg2
from psycopg2 import sql, errors
import uuid
from time import time
import os
import traceback

from app.utilities.db_connection import db_connection
from app.post.post_types import PostTypes
from app.authorization.authorize import authorize_rest
from app.utilities.db_connection import db_connection

from app.api.taxonomy import taxonomy


@taxonomy.route("/api/taxonomy/category/new", methods=["POST"])
@authorize_rest(0)
@db_connection
def create_category(*args, connection, **kwargs):
    if connection is None:
        abort(500)
    filled = json.loads(request.data)
    cur = connection.cursor()

    raw_all_categories = []
    raw_post_categories = []

    try:
        cur.execute(
            sql.SQL("SELECT COUNT(display_name) FROM sloth_taxonomy WHERE post_type = %s AND display_name = %s"),
            [filled["postType"], filled["categoryName"]]
        )
        temp = cur.fetchone()
        if temp[0] > 0:
            filled["slug"] = f"{filled['slug']}-{temp[0]+1}"
        cur.execute(
            sql.SQL("""INSERT INTO sloth_taxonomy (uuid, slug, display_name, post_type, taxonomy_type, lang) 
            VALUES (%s, %s, %s, %s, %s, %s)"""),
            (str(uuid.uuid4()), filled["slug"], filled["categoryName"], filled["postType"], "category",
             filled["language"])
        )
        connection.commit()
        cur.execute(
            sql.SQL("""SELECT uuid, display_name FROM sloth_taxonomy
                                        WHERE post_type = %s"""),
            [filled["postType"]]
        )
        raw_all_categories = cur.fetchall()
        cur.execute(
            sql.SQL("""SELECT uuid FROM sloth_taxonomy
                                WHERE post_type = %s AND uuid IN 
                                (SELECT array_to_string(categories, ',') FROM sloth_posts WHERE uuid = %s)"""),
            [filled["postType"], filled["post"]]
        )
        raw_post_categories = cur.fetchall()
    except Exception as e:
        abort(500)

    post_categories = [cat_uuid for cat in raw_post_categories for cat_uuid in cat]

    all_categories = []
    for category in raw_all_categories:
        selected = False
        if category[0] in post_categories:
            selected: True
        all_categories.append({
            "uuid": category[0],
            "display_name": category[1],
            "selected": selected
        })

    return json.dumps(all_categories)
