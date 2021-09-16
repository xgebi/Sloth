from flask import request, current_app, make_response, abort
import json
from app.authorization.authorize import authorize_rest
from app.utilities.db_connection import db_connection_legacy

from app.api.content_management import content_management


@content_management.route("/api/content/clear", methods=["DELETE"])
@authorize_rest(1)
@db_connection_legacy
def clear_content(*args, connection=None, **kwargs):
    cur = connection.cursor()

    try:
        cur.execute("DELETE FROM sloth_post_taxonomies;")
        cur.execute("DELETE FROM sloth_posts;")
        cur.execute("DELETE FROM sloth_media;")
        cur.execute("DELETE FROM sloth_taxonomy;")
        cur.execute("DELETE FROM sloth_analytics;")
        connection.commit()

        cur.close()
        connection.close()
        response = make_response(json.dumps({"cleaned": True}))
        code = 204
    except Exception as e:
        response = make_response(json.dumps({"cleaned": False}))
        code = 500

    response.headers['Content-Type'] = 'application/json'
    return response, code
