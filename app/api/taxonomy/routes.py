from flask import request, make_response, abort
import json
from psycopg2 import sql
import uuid

from app.authorization.authorize import authorize_rest
from app.utilities.db_connection import db_connection_legacy

from app.api.taxonomy import taxonomy
from app.post.routes import separate_taxonomies


@taxonomy.route("/api/taxonomy/category/new", methods=["POST"])
@authorize_rest(0)
@db_connection_legacy
def create_category(*args, connection, **kwargs):
    if connection is None:
        abort(500)
    filled = json.loads(request.data)
    cur = connection.cursor()

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
            VALUES (%s, %s, %s, %s, %s, %s);"""),
            (str(uuid.uuid4()), filled["slug"], filled["categoryName"], filled["postType"], "category",
             filled["lang"])
        )
        connection.commit()
        cur.execute(
            sql.SQL("""SELECT uuid, display_name, taxonomy_type, slug FROM sloth_taxonomy
                                        WHERE post_type = %s AND lang = %s"""),
            (filled["postType"], filled["lang"])
        )
        raw_all_taxonomies = cur.fetchall()
        cur.execute(
            sql.SQL("""SELECT taxonomy FROM sloth_post_taxonomies
                                                WHERE post = %s"""),
            (None,)
        )
        raw_post_taxonomies = cur.fetchall()
    except Exception as e:
        response = make_response(json.dumps({"error": True}))
        response.headers['Content-Type'] = 'application/json'
        code = 500

        return response, code

    categories, tags = separate_taxonomies(taxonomies=raw_all_taxonomies, post_taxonomies=raw_post_taxonomies)

    response = make_response(json.dumps(categories))
    response.headers['Content-Type'] = 'application/json'
    code = 200

    return response, code
