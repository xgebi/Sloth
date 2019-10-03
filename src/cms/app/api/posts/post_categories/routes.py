from flask import render_template, request, flash, url_for, current_app
from app.api.posts.post_categories import post_categories as post_categories

import json
import psycopg2
from psycopg2 import sql, errors
import uuid
import traceback

from app.utilities.db_connection import db_connection
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize

@post_categories.route("/api/posts/<post_id>/categories-information")
@authorize(0)
@db_connection
def show_categories_list(*args, post_id, connection=None, **kwargs):
	if connection is None:
		abort(500)

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)

	cur = connection.cursor()

	raw_items = []
	try:		
		cur.execute(
			sql.SQL("SELECT uuid, display_name FROM sloth_categories WHERE post_type = %s"), [post_id]
		)
		raw_items = cur.fetchall()
	except Exception as e:
		print(traceback.format_exc())
		abort(500)

	cur.close()
	connection.close()

	categories = []
	for category in raw_items:
		categories.append({
			"uuid": category[0],
			"displayName": category[1]
		})

	return json.dumps({
		"postTypes": postTypesResult,
		"categories": categories
	})