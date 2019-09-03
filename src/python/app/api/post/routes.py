from flask import render_template, request, flash, redirect, url_for, current_app, abort
import json
import psycopg2
from psycopg2 import sql, errors
import uuid
from time import time
import os

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

		cur.execute(
			sql.SQL("SELECT settings_value FROM sloth_settings WHERE settings_name = %s"), ["site_url"]
		)
		url = cur.fetchone()
		cur.close()
	except Exception as e:
		print(e)
		connection.close()
		abort(500)

	connection.close()

	temp_files = [f for f in os.listdir(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content")) if os.path.isfile(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", f)) and f[f.rfind(".") + 1:].lower() in ("jpg", "jpeg", "png", "svg", "bmp", "tiff")]

	files = [url[0] + "/sloth-content/" + f for f in temp_files]

	return json.dumps({ "postTypes": postTypesResult, "postInformation": item, "galleryList": files })

@post.route("/api/posts/<post_id>/new")
@authorize(0)
@db_connection
def prepare_new_post(*args, post_id, connection=None, **kwargs):
	if connection is None:
		abort(500)

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)

	try:
		cur = connection.cursor()
		cur.execute(
			sql.SQL("SELECT settings_value FROM sloth_settings WHERE settings_name = %s"), ["site_url"]
		)
		url = cur.fetchone()
		cur.close()
	except Exception as e:
		print(e)
		connection.close()
		abort(500)

	connection.close()

	temp_files = [f for f in os.listdir(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content")) if os.path.isfile(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", f)) and f[f.rfind(".") + 1:].lower() in ("jpg", "jpeg", "png", "svg", "bmp", "tiff")]

	files = [url[0] + "/sloth-content/" + f for f in temp_files]

	return json.dumps({ "postTypes": postTypesResult, "newPostUuid": str(uuid.uuid4()), "galleryList": files })


@post.route("/api/post/save", methods=['PUT'])
@authorize(0)
@db_connection
def save_post(*args, connection=None, **kwargs):
	if connection is None:
		abort(500)

	data = json.loads(request.data)
	post_data = data["postInfo"]

	item = {}
	post_type_item = {}

	try:
		cur = connection.cursor()
		cur.execute(
			# TODO get slug, categories, tags
			sql.SQL("SELECT uuid FROM sloth_posts WHERE uuid = %s"), [post_data["uuid"]]
		)
		raw_item = cur.fetchone()

		status = "draft" if not data["publish"] else ("scheduled" if data["publish"] and not post_data["publishDate"] else "published")
		
		cur.execute(
			sql.SQL("UPDATE sloth_posts  SET slug = %s, post_type = %s, title = %s, content = %s, css_file = %s, js_file = %s, publish_date = %s, update_date = %s, post_status = %s, tags = %s, categories = %s WHERE uuid = %s"),
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

		query_string = """SELECT uuid, 
							  title,
							  slug, 							   
							  content, 
							  js_file,
							  css_file, 	
							  post_status, 						   
							  publish_date, 
							  update_date, 							  
							  categories,
							  tags 							   
						FROM sloth_posts
						WHERE uuid = %s"""
		if data["publish"]:
			query_string = """SELECT A.uuid AS post_id, 
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
						FROM sloth_posts AS A INNER JOIN sloth_post_types AS B ON B.uuid = A.post_type
						WHERE A.uuid = %s"""


		cur.execute(
			sql.SQL(query_string),
			[post_data["uuid"]]
		)

		raw_item = cur.fetchone()
		
		item_to_generate = {}
		if data["publish"]:
			item_to_generate = {
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
				"post_type_slug": raw_item[12],
				"tags_enabled": raw_item[13],
				"categories_enabled": raw_item[14],
				"archive_enabled": raw_item[15]
			}
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


		cur.close()
	except Exception as e:
		print("Exception", e)
		connection.close()
		abort(500)


	connection.close()
	
	if data["publish"]:
		post_gen = PostsGenerator(item_to_generate, current_app.config)
		post_gen.run() # TODO pass arguments to rename generated folders

	return json.dumps({ "postInformation": item }), 201


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
		cur.execute(
			sql.SQL("SELECT uuid FROM sloth_posts WHERE uuid = %s"), [post_data["uuid"]]
		)
		raw_item = cur.fetchone()

		while raw_item is not None:
			post_data["uuid"] = str(uuid.uuid4())
			cur.execute(
				sql.SQL("SELECT uuid FROM sloth_posts WHERE uuid = %s"), [post_data["uuid"]]
			)
			raw_item = cur.fetchone()
		
		status = "draft" if not data["publish"] else ("published" if data["publish"] else "scheduled")
		if data["publish"] and not post_data.get("publishDate"):
			post_data["publishDate"] = time() * 1000;
		
		cur.execute(
			sql.SQL("INSERT INTO sloth_posts (uuid, slug, post_type, author, title, content, css_file, js_file, publish_date, update_date, post_status, tags, categories, deleted) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'f')"), # possible case for returning
			[
				post_data["uuid"],
				post_data.get("slug") if post_data.get("slug") is not None else "",
				post_data["postType"],
				post_data.get("author") if post_data.get("author") is not None else "",
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

		query_string = """SELECT uuid, 
							  title,
							  slug, 							   
							  content, 
							  js_file,
							  css_file, 	
							  post_status, 						   
							  publish_date, 
							  update_date, 							  
							  categories,
							  tags, 							   
						FROM sloth_posts
						WHERE uuid = %s"""
		if data["publish"]:
			query_string = """SELECT A.uuid AS post_id, 
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
						FROM sloth_posts AS A INNER JOIN sloth_post_types AS B ON B.uuid = A.post_type
						WHERE A.uuid = %s"""


		cur.execute(
			sql.SQL(query_string),
			[post_data["uuid"]]
		)

		raw_item = cur.fetchone()
		
		item_to_generate = {}
		if data["publish"]:
			item_to_generate = {
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
				"post_type": raw_item[11],
				"post_type_slug": raw_item[12],
				"tags_enabled": raw_item[13],
				"categories_enabled": raw_item[14],
				"archive_enabled": raw_item[15]
			}
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


		cur.close()
	except Exception as e:
		print("Exception", e)
		connection.close()
		abort(500)


	connection.close()
	
	if data["publish"]:
		post_gen = PostsGenerator(item_to_generate, current_app.config)
		post_gen.run()

	return json.dumps({ "postInformation": item }), 201
