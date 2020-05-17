from flask import request, flash, url_for, current_app, abort, redirect, render_template
import psycopg2
from psycopg2 import sql

import app
import os
from pathlib import Path
import bcrypt
import json

from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web

from app.posts.post_types import PostTypes

from app.web.settings.themes import settings_themes

@settings_themes.route("/settings/themes")
@authorize_web(1)
@db_connection
def show_theme_settings(*args, permission_level, connection, **kwargs):
	if connection is None:
		return render_toe(template="settings-themes.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data={ "error": "No connection to database" })
	settings = {}

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)
	
	config = current_app.config

	cur = connection.cursor()

	active_theme = ""
	try:		
		cur.execute(
			"SELECT settings_value FROM sloth_settings WHERE settings_name = 'active_theme'"
		)
		raw_items = cur.fetchone()
		active_theme = raw_items[0]
	except Exception as e:
		print("db error")
		abort(500)

	cur.close()
	connection.close()

	listOfDirs = os.listdir(config["THEMES_PATH"])
	themes = []	

	for folder in listOfDirs:
		theme_file = Path(config["THEMES_PATH"], folder, 'theme.json')
		if (theme_file.is_file()):
			with open(theme_file, 'r') as f:
				theme = json.loads(f.read())
				if (theme["choosable"] and theme["name"].find(" ") == -1):
					themes.append(theme)
	import pdb; pdb.set_trace()	
	return render_template("themes-list.html", post_types=postTypesResult, permission_level=permission_level, themes=themes)

@settings_themes.route("/settings/themes/activate/<theme_name>")
@authorize_web(1)
@db_connection
def save_active_theme_settings(*args, theme_name, connection=None, **kwargs):
	pass