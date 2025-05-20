import psycopg
from flask import make_response
import json
from app.authorization.authorize import authorize_rest
from app.utilities.db_connection import db_connection

from app.routes.content_management import content_management


@content_management.route("/api/content/clear", methods=["DELETE"])
@authorize_rest(1)
@db_connection
def clear_content(*args, connection: psycopg.Connection, **kwargs):

	try:
		with connection.cursor() as cur:
			cur.execute("DELETE FROM sloth_post_taxonomies;")
			cur.execute("DELETE FROM sloth_posts;")
			cur.execute("DELETE FROM sloth_media;")
			cur.execute("DELETE FROM sloth_taxonomy;")
			cur.execute("DELETE FROM sloth_analytics;")
			connection.commit()

		response = make_response(json.dumps({"cleaned": True}))
		code = 204
	except Exception as e:
		response = make_response(json.dumps({"cleaned": False}))
		code = 500
	connection.close()
	response.headers['Content-Type'] = 'application/json'
	return response, code
