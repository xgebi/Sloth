from flask import request, flash, url_for, current_app, abort, redirect
import psycopg2
from psycopg2 import sql
from toes.toes import render_toe
from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web

from app.posts.post_types import PostTypes

from app.web.settings import settings

@settings.route("/settings/themes")
@authorize_web(1)
@db_connection
def show_theme_settings(*args, connection, **kwargs):
	if connection is None:
		return render_toe(template="settings_themes.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data={ "error": "No connection to database" })
	settings = {}

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)

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
				if (theme["choosable"]):
					themes.append(theme)

	return render_toe(template="settings_themes.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data={ "themes": themes, "post_types": postTypesResult })