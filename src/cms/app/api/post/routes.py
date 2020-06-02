from flask import request, flash, url_for, current_app, abort
import json
import psycopg2
from psycopg2 import sql, errors
import uuid
from time import time
import os
import traceback

from app.utilities.db_connection import db_connection
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize_rest
from app.utilities.db_connection import db_connection
from app.posts.posts_generator import PostsGenerator

from app.api.post import post

reserved_folder_names = ('tag', 'category')


@post.route("/api/post/media", methods=["GET"])
@authorize_rest(0)
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
	
	return json.dumps({})


@post.route("/api/post/upload-file", methods=['POST'])
@authorize_rest(0)
@db_connection
def upload_image(*args, file_name, connection=None, **kwargs):
	ext = file_name[file_name.rfind("."):]
	if not ext.lower() in (".png", ".jpg", ".jpeg", ".svg", ".bmp", ".tiff"):
		abort(500)
	with open(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", file_name), 'wb') as f:
		f.write(request.data)

	url = ""

	try:
		cur = connection.cursor()
		cur.execute(
			sql.SQL("SELECT settings_value FROM sloth_settings WHERE settings_name = %s"), ["site_url"]
		)
		url = cur.fetchone()
		cur.close()
	except Exception as e:
		print(traceback.format_exc())
		connection.close()
		abort(500)
	
	temp_files = [f for f in os.listdir(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content")) if os.path.isfile(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", f)) and f[f.rfind(".") + 1:].lower() in ("jpg", "jpeg", "png", "svg", "bmp", "tiff")]

	files = [url[0] + "/sloth-content/" + f for f in temp_files]

	return json.dumps({ "galleryList": files }), 201