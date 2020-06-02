from flask import request, flash, url_for, current_app, abort, redirect, render_template
from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web
from app.posts.post_types import PostTypes
import psycopg2
from psycopg2 import sql
import datetime
import uuid

from app.web.post import post

@post.route("/post/<post_type>")
@authorize_web(0)
@db_connection
def show_posts_list(*args, permission_level, connection, post_type, **kwargs):
	if connection is None:
		return redirect("/database-error")	
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
def show_post_edit(*args, permission_level, connection, post_id, **kwargs):	
	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)

	cur = connection.cursor()
	media = []
	post_type_name = ""
	post = {}
	try:
		cur.execute(
			sql.SQL("SELECT uuid, file_path, alt FROM sloth_media")
		)	
		media = cur.fetchall()		

		cur.execute(
			sql.SQL("SELECT A.title, A.content, A.excerpt, A.css, A.js, A.thumbnail, A.publish_date, A.update_date, A.post_status, A.tags, A.categories, B.display_name, A.post_type FROM sloth_posts AS A INNER JOIN sloth_users AS B ON A.author = B.uuid WHERE A.uuid = %s"),
			[post_type]
		)
		post = cur.fetchone()

		cur.execute(
			sql.SQL("SELECT lang, slug, post_type, FROM sloth_post_types WHERE uuid = %s"),
			[post[12]]
		)
		post_type_name = cur.fetchone()[0]
	except Exception as e:
		print("db error")
		abort(500)

	cur.close()
	connection.close()

	token = uuid.uuid4()

	data = {
		"title": post[0],
		"excerpt": post[1],
		"description": post[2],
		"css": post[3],
		"js": post[4],
		"thumbnail": post[5],
		"publish_date": post[6],
		"update_date": post[7],
		"post_status": post[8],
		"tags": post[9],
		"categories": post[10],
		"display_name": post[11]
	}	

	return render_template("post-edit.html", post_types=postTypesResult, permission_level=permission_level, token=token, post_type_name=post_type_name, data=data)

@post.route("/post/<post_type>/new")
@authorize_web(0)
@db_connection
def show_post_new(*args, permission_level, connection, post_type, **kwargs):	
	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)

	cur = connection.cursor()
	media = []
	try:

		cur.execute(
			sql.SQL("SELECT uuid, file_path, alt FROM sloth_media")
		)	
		media = cur.fetchall()
		cur.execute(
			sql.SQL("SELECT display_name FROM sloth_post_types WHERE uuid = %s"),
			[post_type]
		)
		post_type_name = cur.fetchone()[0]
	except Exception as e:
		print("db error")
		abort(500)

	cur.close()
	connection.close()

	token = uuid.uuid4()
	
	return render_template("post-edit.html", post_types=postTypesResult, permission_level=permission_level, token=token, post_type_name=post_type_name, data={"new": True})

@post.route("/post/<post_id>/save", methods=["POST", "PUT"])
@authorize_web(0)
@db_connection
def save_post(*args, permission_level, connection, post_id, **kwargs):	
	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)

	cur = connection.cursor()
	media = []
	post_type_name = ""
	post = {}
	try:
		cur.execute(
			sql.SQL("SELECT uuid, file_path, alt FROM sloth_media")
		)	
		media = cur.fetchall()		

		cur.execute(
			sql.SQL("SELECT A.title, A.content, A.excerpt, A.css, A.js, A.thumbnail, A.publish_date, A.update_date, A.post_status, A.tags, A.categories, B.display_name, A.post_type FROM sloth_posts AS A INNER JOIN sloth_users AS B ON A.author = B.uuid WHERE A.uuid = %s"),
			[post_type]
		)
		post = cur.fetchone()

		cur.execute(
			sql.SQL("SELECT lang, slug, post_type, FROM sloth_post_types WHERE uuid = %s"),
			[post[12]]
		)
		post_type_name = cur.fetchone()[0]
	except Exception as e:
		print("db error")
		abort(500)

	cur.close()
	connection.close()

	token = uuid.uuid4()

	data = {
		"title": post[0],
		"excerpt": post[1],
		"description": post[2],
		"css": post[3],
		"js": post[4],
		"thumbnail": post[5],
		"publish_date": post[6],
		"update_date": post[7],
		"post_status": post[8],
		"tags": post[9],
		"categories": post[10],
		"display_name": post[11]
	}	

	return render_template("post-edit.html", post_types=postTypesResult, permission_level=permission_level, token=token, post_type_name=post_type_name, data=data)

@post.route("/post/<type_id>/taxonomy")
@authorize_web(0)
@db_connection
def show_post_taxonomy(*args, permission_level, connection, type_id, **kwargs):	
	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)

	cur = connection.cursor()
	taxonomy = []
	try:		
		cur.execute(
			sql.SQL("SELECT uuid, slug, display_name, taxonomy_type FROM sloth_taxonomy WHERE post_type = %s"), [type_id]
		)	
		taxonomy = cur.fetchall()
	except Exception as e:
		import pdb; pdb.set_trace()
		print("db error")
		abort(500)

	cur.close()
	connection.close()

	
	
	return render_template("taxonomy-list.html", post_types=postTypesResult, permission_level=permission_level, token=token)