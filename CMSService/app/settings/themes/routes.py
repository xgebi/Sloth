from flask import request, current_app, abort, redirect
from werkzeug import utils as w_utils
import psycopg
import os
from pathlib import Path
import json
import zipfile
import shutil

from app.toes.toes import render_toe_from_path
from app.utilities.db_connection import db_connection
from app.utilities.utilities import get_default_language
from app.authorization.authorize import authorize_web, authorize_rest
from app.back_office.post.post_generator import PostGenerator
from app.toes.hooks import Hooks

from app.back_office.post.post_types import PostTypes

from app.settings.themes import settings_themes


@settings_themes.route("/settings/themes")
@authorize_web(1)
@db_connection
def show_theme_settings(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
	post_types = PostTypes()
	post_types_result = post_types.get_post_type_list(connection)
	config = current_app.config

	try:
		with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
			cur.execute(
				"SELECT settings_value FROM sloth_settings WHERE settings_name = 'active_theme'"
			)
			raw_items = cur.fetchone()
			active_theme = raw_items['settings_value']
	except Exception:
		connection.close()
		print("db error")
		abort(500)

	default_language = get_default_language(connection=connection)
	connection.close()

	list_of_dirs = os.listdir(config["THEMES_PATH"])
	themes = []

	for folder in list_of_dirs:
		theme_file = Path(config["THEMES_PATH"], folder, 'theme.json')
		if theme_file.is_file():
			with open(theme_file, 'r') as f:
				theme = json.loads(f.read())
				if theme["choosable"] and theme["name"].find(" ") == -1:
					themes.append(theme)

	return render_toe_from_path(
		path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
		template="theme-list.toe.html",
		data={
			"title": "List of themes",
			"post_types": post_types_result,
			"permission_level": permission_level,
			"default_lang": default_language,
			"themes": themes,
			"active_theme": active_theme,
			"regenerating": Path(os.path.join(os.getcwd(), 'generating.lock')).is_file(),
		},
		hooks=Hooks()
	)


@settings_themes.route("/settings/themes/activate/<theme_name>")
@authorize_web(1)
@db_connection
def save_active_theme_settings(*args, theme_name: str, connection: psycopg.Connection, **kwargs):
	"""
	Sets an active theme

	:param args:
	:param theme_name:
	:param connection:
	:param kwargs:
	:return:
	"""
	# save theme theme to database
	try:
		with connection.cursor() as cur:
			cur.execute("UPDATE sloth_settings SET settings_value = %s WHERE settings_name = 'active_theme';",
						(theme_name, ))
			connection.commit()
	except Exception as e:
		print("db error")
		connection.close()
		abort(500)
	connection.close()
	# regenerate all post
	posts_gen = PostGenerator()
	posts_gen.run(everything=True)

	return redirect("/settings/themes")


@settings_themes.route("/api/upload-theme", methods=["POST"])
@authorize_rest(1)
def upload_theme(*args, **kwargs):
	"""
	API endpoint for uploading a theme

	:param args:
	:param kwargs:
	:return:
	"""
	theme = request.files["image"]
	if theme.mimetype == 'application/x-zip-compressed' and theme.filename.endswith(".zip"):
		path = os.path.join(current_app.config["THEMES_PATH"], theme.filename[:theme.filename.rfind(".zip")])
		if os.path.isdir(path):
			shutil.rmtree(path)
		with open(os.path.join(current_app.config["THEMES_PATH"], w_utils.secure_filename(theme.filename)), 'wb') as f:
			theme.save(os.path.join(current_app.config["THEMES_PATH"], w_utils.secure_filename(theme.filename)))
		os.makedirs(path)
		with zipfile.ZipFile(os.path.join(current_app.config["THEMES_PATH"], w_utils.secure_filename(theme.filename)), 'r') as zip_ref:
			zip_ref.extractall(current_app.config["THEMES_PATH"])
		os.remove(os.path.join(current_app.config["THEMES_PATH"], w_utils.secure_filename(theme.filename)))
		return json.dumps({"theme_uploaded": theme.filename[:theme.filename.rfind(".zip")]}), 201
	else:
		abort(500)


@settings_themes.route("/api/themes/list", methods=["GET"])
@authorize_rest(1)
@db_connection
def show_themes_list(*args, connection: psycopg.Connection, **kwargs):
	"""
	API endpoint that returns JSON with list of themes
	:param args:
	:param connection:
	:param kwargs:
	:return:
	"""
	config = current_app.config

	list_of_dirs = os.listdir(config["THEMES_PATH"])
	themes = []

	for folder in list_of_dirs:
		theme_file = Path(config["THEMES_PATH"], folder, 'theme.json')
		if theme_file.is_file():
			with open(theme_file, 'r') as f:
				theme = json.loads(f.read())
				if theme["choosable"]:
					themes.append(theme)

	connection.close()
	return json.dumps({"themes": themes})
