from flask import render_template, request, flash, redirect, url_for, current_app
from app.api.themes import themes as themes
import app

import psycopg2
from psycopg2 import sql
import bcrypt
import json
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize
from app.utilities.db_connection import db_connection

@themes.route("/api/themes/list", methods=["GET"])
@authorize(1)
@db_connection
def show_themes_list(*args, connection=None, **kwargs):
	if connection is None:
		abort(500)

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)

	config = current_app.config
	print(config["THEMES_PATH"])
	
	connection.close()
	return json.dumps({ "postTypes": postTypesResult })