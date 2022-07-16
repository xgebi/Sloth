import json
import psycopg
import uuid
from flask import request, make_response

from app.api.taxonomy import taxonomy
from app.authorization.authorize import authorize_rest
from app.routes.post.routes import separate_taxonomies
from app.utilities.db_connection import db_connection


@taxonomy.route("/api/taxonomy/category/new", methods=["POST"])
@authorize_rest(0)
@db_connection
def create_category(*args, connection: psycopg.Connection, **kwargs):
	filled = json.loads(request.data)

	try:
		with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
			cur.execute("""SELECT COUNT(display_name) FROM sloth_taxonomy WHERE post_type = %s AND display_name = %s""",
						(filled["postType"], filled["categoryName"]))
			count = cur.fetchone()['count']
			if count > 0:
				filled["slug"] = f"{filled['slug']}-{count + 1}"
			cur.execute("""INSERT INTO sloth_taxonomy (uuid, slug, display_name, post_type, taxonomy_type, lang) 
                VALUES (%s, %s, %s, %s, %s, %s);""",
						(str(uuid.uuid4()), filled["slug"], filled["categoryName"], filled["postType"], "category",
						 filled["lang"]))
			connection.commit()
			cur.execute("""SELECT uuid, display_name, taxonomy_type, slug FROM sloth_taxonomy
                                            WHERE post_type = %s AND lang = %s""",
						(filled["postType"], filled["lang"])
						)
			all_taxonomies = cur.fetchall()
			cur.execute("""SELECT taxonomy FROM sloth_post_taxonomies WHERE post = %s""",
						(None,)
						)
			post_taxonomies = cur.fetchall()
	except Exception as e:
		response = make_response(json.dumps({"error": True}))
		response.headers['Content-Type'] = 'application/json'
		code = 500
		connection.close()
		return response, code

	categories, tags = separate_taxonomies(taxonomies=all_taxonomies, post_taxonomies=post_taxonomies)
	connection.close()
	response = make_response(json.dumps(categories))
	response.headers['Content-Type'] = 'application/json'
	code = 200

	return response, code
