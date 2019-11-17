from flask import request, flash, url_for, current_app
from app.api.themes import themes as themes
import app
import os
from pathlib import Path
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

	listOfDirs = os.listdir(config["THEMES_PATH"])
	themes = []	

	for folder in listOfDirs:
		theme_file = Path(config["THEMES_PATH"], folder, 'theme.json')
		if (theme_file.is_file()):
			with open(theme_file, 'r') as f:
				theme = json.loads(f.read())
				if (theme["choosable"]):
					themes.append(theme)
	
	connection.close()
	return json.dumps({ "postTypes": postTypesResult, "themes": themes })