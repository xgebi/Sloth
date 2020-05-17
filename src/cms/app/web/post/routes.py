from flask import request, flash, url_for, current_app, abort, redirect, render_template
from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web
from app.posts.post_types import PostTypes
import psycopg2
from psycopg2 import sql
import datetime

from app.web.post import post

@post.route("/post/<post_type>")
@authorize_web(0)
@db_connection
def show_posts_list(*args, permission_level, connection, post_type, **kwargs):
	if connection is None:
		return render_toe(template="settings.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data={ "error": "No connection to database" })
	post_type_info = {
		"uuid": post_type
	}

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)

	cur = connection.cursor()

	raw_items = []
	# uuid, post_type, title, publish_date, update_date, post_status, categories, deleted
	try:
		cur.execute(
			sql.SQL("SELECT display_name FROM sloth_post_types WHERE uuid = %s"), [post_type]
		)	

		post_type_info["name"] = cur.fetchall()[0][0]
		cur.execute(
			sql.SQL("SELECT A.uuid, A.title, A.publish_date, A.update_date, A.post_status, B.display_name FROM sloth_posts AS A INNER JOIN sloth_users AS B ON A.author = B.uuid WHERE A.deleted = %s AND A.post_type = %s"), [False, post_type]
		)
		raw_items = cur.fetchall()
	except Exception as e:
		print("db error")
		abort(500)

	cur.close()
	connection.close()

	items = []
	for item in raw_items:
		items.append({
			"uuid": item[0],
			"title": item[1],
			"publish_date": datetime.datetime.fromtimestamp(float(item[2])/1000.0).strftime("%Y-%m-%d"),
			"update_date": datetime.datetime.fromtimestamp(float(item[3])/1000.0).strftime("%Y-%m-%d"),
			"status": item[4],
			"author": item[5]
		})

	return render_template("post-list.html", post_types=postTypesResult, permission_level=permission_level, post_list=items, post_type=post_type_info)

@post.route("/post/<post_id>/edit")
@authorize_web(0)
@db_connection
def show_post_edit(permission_level, connection, post_id, action):	
	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)
	post_type_info = {
		"uuid": post_type
	}

	cur = connection.cursor()
	media = []
	try:
		cur.execute(
			sql.SQL("SELECT uuid, secondary_uuid, original_lang_entry_uuid, lang, slug, post_type, author, title, content, description, css, js, thumbnail, publish_date, update_date, post_status, tags, categories FROM sloth_posts WHERE uuid = %", [post_id])
		)

		cur.execute(
			sql.SQL("SELECT uuid, file_path, alt FROM sloth_media")
		)	
		media = cur.fetchall()
	except Exception as e:
		print("db error")
		abort(500)

	cur.close()
	connection.close()

	token = "aaaaaa"
	import pdb; pdb.set_trace()
	return render_template("post-edit.html", post_types=postTypesResult, post_type=post_type_info, permission_level=permission_level, token=token, uuid=post_id)

@post.route("/post/<post_id>/new")
@authorize_web(0)
@db_connection
def show_post_new(permission_level, connection, post_id, action):	
	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)
	post_type_info = {
		"uuid": post_type
	}

	cur = connection.cursor()
	media = []
	try:
		cur.execute(
			sql.SQL("SELECT uuid, secondary_uuid, original_lang_entry_uuid, lang, slug, post_type, author, title, content, description, css, js, thumbnail, publish_date, update_date, post_status, tags, categories FROM sloth_posts WHERE uuid = %", [post_id])
		)

		cur.execute(
			sql.SQL("SELECT uuid, file_path, alt FROM sloth_media")
		)	
		media = cur.fetchall()
	except Exception as e:
		print("db error")
		abort(500)

	cur.close()
	connection.close()

	token = "aaaaaa"
	import pdb; pdb.set_trace()
	return render_template("post-edit.html", post_types=postTypesResult, post_type=post_type_info, permission_level=permission_level, token=token, uuid=post_id)

@post.route("/post/<type_id>/taxonomy")
@authorize_web(0)
@db_connection
def show_post_taxonomy(*args, permission_level, connection, type_id, **kwargs):	
	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)

	cur = connection.cursor()
	media = []
	try:
		cur.execute(
			sql.SQL("SELECT uuid, secondary_uuid, original_lang_entry_uuid, lang, slug, post_type, author, title, content, description, css, js, thumbnail, publish_date, update_date, post_status, tags, categories FROM sloth_posts WHERE uuid = %", [type_id])
		)

		cur.execute(
			sql.SQL("SELECT uuid, file_path, alt FROM sloth_media")
		)	
		media = cur.fetchall()
	except Exception as e:
		print("db error")
		abort(500)

	cur.close()
	connection.close()

	token = "aaaaaa"
	import pdb; pdb.set_trace()
	return render_template("post-edit.html", post_types=postTypesResult, post_type=post_type_info, permission_level=permission_level, token=token, uuid=post_id)