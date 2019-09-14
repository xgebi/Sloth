from flask import render_template, request, flash, redirect, url_for, current_app, abort
import json
import psycopg2
from psycopg2 import sql, errors
import uuid

from app.utilities.db_connection import db_connection
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize
from app.posts.posts_generator import PostsGenerator

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
			sql.SQL("SELECT uuid, title, post_status, publish_date, update_date, categories, tags FROM sloth_posts WHERE post_type = %s AND deleted <> true OR deleted IS null"), [post_id]
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

	current_post_type = {}
	for post_type in postTypesResult:
		if (post_type["uuid"] == post_id):
			current_post_type = post_type
			break

	connection.close()
	return json.dumps({ "currentPostType": current_post_type, "postTypes": postTypesResult, "posts": items })

@posts_list.route("/api/posts/<post_id>/delete")
@authorize(0)
@db_connection
def delete_post(*args, post_id, connection=None, **kwargs):
	# get post information from database - post slug, categories, tags and post type slug
	item = {}
	try:
		cur = connection.cursor()

		cur.execute(
			sql.SQL("SELECT A.slug, A.categories, A.tags, B.slug FROM sloth_posts AS A INNER JOIN sloth_post_types AS B ON A.post_type = B.uuid WHERE A.uuid = %s"), [post_id]
		)
		raw_item = cur.fetchone()		

		item = {
			"post_slug": raw_item[0],				
			"categories": raw_item[1],
			"tags": raw_item[2],
			"post_type_slug": raw_item[3]
		}
		# delete post from database
		cur.execute(
			sql.SQL("DELETE FROM sloth_posts WHERE uuid = %s"), [post_id]
		)
		cur.close()
	except Exception as e:
		print(e)
		connection.close()
		abort(500)

	generator = PostsGenerator(current_app.config)
	generator.delete_post(item)	
	