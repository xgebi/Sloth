from flask import render_template, request, flash, redirect, url_for, current_app, abort
import json
import psycopg2
from psycopg2 import sql, errors
import uuid

from app.utilities.db_connection import db_connection
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize
from app.utilities.db_connection import db_connection
from app.posts.posts_generator import PostsGenerator

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
			sql.SQL("SELECT uuid, title, slug, content, js_file, css_file, post_status, publish_date, update_date, categories, tags FROM sloth_posts WHERE uuid = %s"), [post_id]
		)
		raw_item = cur.fetchone()
		cur.close()

		item = {
			"uuid": raw_item[0],
			"title": raw_item[1],
			"slug": raw_item[2],
			"content": raw_item[3],
			"jsFilePath": raw_item[4],
			"cssFilePath": raw_item[5],
			"postStatus": raw_item[6],
			"publishDate": raw_item[7],
			"updateDate": raw_item[8],
			"categories": raw_item[9],
			"tags": raw_item[10]
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


@post.route("/api/post/save", methods=['PUT'])
@authorize(0)
@db_connection
def save_post(*args, connection=None, **kwargs):
	if connection is None:
		abort(500)

	data = json.loads(request.data)
	import pdb; pdb.set_trace()

	try:
		cur = connection.cursor()

		cur.execute(
			sql.SQL("UPDATE sloth_posts SET uuid = %s, title = %s, slug = %s, content = %s, js_file = %s, css_file = %s, post_status = %s, publish_date = %s, update_date = %s, categories = %s, tags = %s WHERE uuid = %s"), [post_id]
		)
		raw_item = cur.fetchone()
		cur.close()

		item = {
			"uuid": raw_item[0],
			"title": raw_item[1],
			"slug": raw_item[2],
			"content": raw_item[3],
			"jsFilePath": raw_item[4],
			"cssFilePath": raw_item[5],
			"postStatus": raw_item[6],
			"publishDate": raw_item[7],
			"updateDate": raw_item[8],
			"categories": raw_item[9],
			"tags": raw_item[10]
		}
	except Exception as e:
		print(e)
		connection.close()
		abort(500)


	connection.close()
	return json.dumps({ "postTypes": postTypesResult, "newPostUuid": str(uuid.uuid4()) })

@post.route("/api/post/create", methods=['POST'])
@authorize(0)
@db_connection
def create_new_post(*args, connection=None, **kwargs):
	if connection is None:
		abort(500)

	data = json.loads(request.data)
	post_data = data["postInfo"]

	item = {}
	post_type_item = {}

	try:
		cur = connection.cursor()

		# TODO here must be insert instead
		cur.execute(
			# uuid, slug, post_type, title, content, css_file, js_file, publish_date, update_date, post_status, tags, categories, deleted
			#sql.SQL("INSERT INTO sloth_posts VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'f')"), [post_id]
			sql.SQL("SELECT uuid FROM sloth_posts WHERE uuid = %s"), [post_data["uuid"]]
		)
		raw_item = cur.fetchone()

		while raw_item is not None:
			post_data["uuid"] = str(uuid.uuid4())
			cur.execute(
				sql.SQL("SELECT uuid FROM sloth_posts WHERE uuid = %s"), [post_data["uuid"]]
			)
			raw_item = cur.fetchone()

		status = "draft" if not data["publish"] else ("scheduled" if data["publish"] and not post_data["publishDate"] else "published")
		
		cur.execute(
			sql.SQL("INSERT INTO sloth_posts (uuid, slug, post_type, title, content, css_file, js_file, publish_date, update_date, post_status, tags, categories, deleted) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'f')"), 
			[
				post_data["uuid"],
				post_data.get("slug") if post_data.get("slug") is not None else "",
				post_data["postType"],
				post_data.get("title") if post_data.get("title") is not None else "",
				post_data.get("content") if post_data.get("content") is not None else "",
				post_data.get("cssFile") if post_data.get("cssFile") is not None else "",
				post_data.get("jsFile") if post_data.get("jsFile") is not None else "",
				post_data.get("publishDate"),
				post_data.get("updateDate"),
				status,
				post_data.get("tags") if post_data.get("tags") is not None else [],
				post_data.get("categories") if post_data.get("categories") is not None else [],

			]
		)
		connection.commit()

		cur.execute(
			sql.SQL("""SELECT A.uuid AS post_id, 
							  A.title,
							  A.slug, 							   
							  A.content, 
							  A.js_file,
							  A.css_file, 	
							  A.post_status, 						   
							  A.publish_date, 
							  A.update_date, 							  
							  A.categories,
							  A.tags, 							   
							  B.uuid AS post_type_id, 
							  B.slug AS post_type_slug, 
							  B.tags_enabled, 
							  B.categories_enabled, 
							  B.archive_enabled 
						FROM sloth_posts AS A INNER JOIN sloth_post_types AS B ON A.post_type = B.uuid 
						WHERE A.uuid = %s"""),
			[post_data["uuid"]]
		)

		raw_item = cur.fetchone()
		item = {
			"uuid": raw_item[0],
			"title": raw_item[1],
			"slug": raw_item[2],
			"content": raw_item[3],
			"jsFilePath": raw_item[4],
			"cssFilePath": raw_item[5],
			"postStatus": raw_item[6],
			"publishDate": raw_item[7],
			"updateDate": raw_item[8],
			"categories": raw_item[9],
			"tags": raw_item[10],
			"post_type_slug": raw_post_type[12],
			"tags_enabled": raw_post_type[13],
			"categories_enabled": raw_post_type[14],
			"archive_enabled": raw_post_type[15]
		}


		cur.close()


		post_type_item = {
			"slug": raw_post_type[0],
			"tags": raw_post_type[1],
			"categories": raw_post_type[2],
			"archive": raw_post_type[3]
		}
	except Exception as e:
		print("Exception", e)
		connection.close()
		abort(500)


	connection.close()

	post_gen = PostsGenerator(item, post_type_item)
	post_gen.run()

	return json.dumps({ "postInformation": item }), 201
