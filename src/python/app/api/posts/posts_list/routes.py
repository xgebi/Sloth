from flask import render_template, request, flash, redirect, url_for, current_app, abort
import json
import psycopg2
from psycopg2 import sql, errors

from app.utilities.db_connection import db_connection
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize
from app.utilities.db_connection import db_connection

from app.api.posts.posts_list import posts_list


@posts_list.route("/api/posts/<post_id>/list")
@authorize(0)
@db_connection
def show_posts_list(*args, post_id, connection=None, **kwargs):
	if connection is None:
		abort(500)

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)
	
	items = []
	try:
		cur = connection.cursor()

		cur.execute(
			sql.SQL("SELECT uuid, title, post_status, publish_date, update_date, categories, tags FROM sloth_posts WHERE post_type = %s"), [post_id]
		)
		raw_items = cur.fetchall()
		cur.close()

		for item in raw_items:
			items.append({
				"uuid": item[0],
				"title": item[1],
				"postStatus": item[2],
				"publishDate": item[3],
				"updateDate": item[4],
				"categories": item[5],
				"tags": item[6]
			})
	except Exception as e:
		print(e)
		connection.close()
		abort(500)

	connection.close()
	return json.dumps({ "postTypes": postTypesResult, "posts": items })