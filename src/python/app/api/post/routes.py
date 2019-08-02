from flask import render_template, request, flash, redirect, url_for, current_app, abort
import json
import psycopg2
from psycopg2 import sql, errors
import uuid

from app.utilities.db_connection import db_connection
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize
from app.utilities.db_connection import db_connection

from app.api.post import post


@post.route("/api/post/<post_id>/edit")
@authorize(0)
@db_connection
def get_post_information(*args, post_id, connection=None, **kwargs):
	if connection is None:
		abort(500)

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)

	item = {}
	try:
		cur = connection.cursor()

		cur.execute(
			sql.SQL("SELECT uuid, title, post_status, publish_date, update_date, categories, tags FROM sloth_posts WHERE uuid = %s"), [post_id]
		)
		raw_item = cur.fetchone()
		cur.close()

		item = {
			"uuid": raw_item[0],
			"title": raw_item[1],
			"postStatus": raw_item[2],
			"publishDate": raw_item[3],
			"updateDate": raw_item[4],
			"categories": raw_item[5],
			"tags": raw_item[6]
		}
	except Exception as e:
		print(e)
		connection.close()
		abort(500)

	connection.close()
	return json.dumps({ "postTypes": postTypesResult, "postInformation": item })

@post.route("/api/posts/<post_id>/new")
@authorize(0)
@db_connection
def prepare_new_post(*args, post_id, connection=None, **kwargs):
	if connection is None:
		abort(500)

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)

	connection.close()
	return json.dumps({ "postTypes": postTypesResult, "newPostUuid": str(uuid.uuid4()) })