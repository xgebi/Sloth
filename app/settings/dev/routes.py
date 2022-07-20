import json
import os
import traceback
from pathlib import Path

import psycopg
from flask import abort, make_response, current_app

from app.authorization.authorize import authorize_web
from app.back_office.post.post_types import PostTypes
from app.settings.dev import dev_settings
from app.toes.hooks import Hooks
from app.toes.toes import render_toe_from_path
from app.utilities.utilities import get_default_language
from app.utilities.db_connection import db_connection


@dev_settings.route("/settings/dev")
@authorize_web(1)
@db_connection
def show_dev_settings(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
	"""
	Renders a page with developer settings

	:param args:
	:param permission_level:
	:param connection:
	:param kwargs:
	:return:
	"""
	post_types = PostTypes()
	post_types_result = post_types.get_post_type_list(connection)

	default_language = get_default_language(connection=connection)
	connection.close()

	if os.environ["FLASK_ENV"] != "development":
		return render_toe_from_path(
			path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
			template="dev-settings-prod.toe.html",
			data={
				"title": "Dev Settings",
				"post_types": post_types_result,
				"permission_level": permission_level,
				"default_lang": default_language
			},
			hooks=Hooks()
		)
	return render_toe_from_path(
		path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
		template="dev-settings.toe.html",
		data={
			"title": "Dev Settings",
			"post_types": post_types_result,
			"permission_level": permission_level,
			"default_lang": default_language
		},
		hooks=Hooks()
	)


@dev_settings.route("/api/settings/dev/posts", methods=["DELETE"])
@authorize_web(1)
@db_connection
def delete_posts(*args, connection: psycopg.Connection, **kwargs):
	"""
	Deletes all posts and related items

	:param args:
	:param connection:
	:param kwargs:
	:return:
	"""
	if os.environ["FLASK_ENV"] != "development":
		abort(403)

	try:
		with connection.cursor() as cur:
			cur.execute("""DELETE FROM sloth_post_sections;""")
			cur.execute("""DELETE FROM sloth_post_taxonomies;""")
			cur.execute("""DELETE FROM sloth_post_libraries;""")
			cur.execute("""DELETE FROM sloth_posts;""")
			connection.commit()

		connection.close()

		response = make_response(json.dumps(
			{"postsDeleted": True}
		))
		code = 200
	except Exception as e:
		print(e)
		traceback.print_exc()
		response = make_response(json.dumps(
			{"postsDeleted": False}
		))
		code = 500

	response.headers['Content-Type'] = 'application/json'
	return response, code


@dev_settings.route("/api/settings/dev/taxonomy", methods=["DELETE"])
@authorize_web(1)
@db_connection
def delete_taxonomy(*args, connection: psycopg.Connection, **kwargs):
	"""
	API endpoint for deleting all taxonomy

	:param args:
	:param connection:
	:param kwargs:
	:return:
	"""
	code = -1
	if os.environ["FLASK_ENV"] != "development":
		response = make_response(json.dumps(
			{"taxonomyDeleted": False}
		))
		code = 403

	if code == -1:
		try:
			with connection.cursor() as cur:
				cur.execute("""DELETE FROM sloth_taxonomy;""")
				connection.commit()

			response = make_response(json.dumps(
				{"taxonomyDeleted": True}
			))
			code = 200
		except Exception as e:
			print(e)
			traceback.print_exc()
			response = make_response(json.dumps(
				{"taxonomyDeleted": False}
			))
			code = 500
		connection.close()

	response.headers['Content-Type'] = 'application/json'
	return response, code


@dev_settings.route("/api/settings/dev/health-check", methods=["GET"])
@authorize_web(0)
@db_connection
def check_posts_health(*args, connection: psycopg.Connection, **kwargs):
	if connection is None:
		response = make_response(json.dumps(
			{"urls": []}
		))
		code = 500
	else:
		try:
			with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
				# from settings get default language
				cur.execute("""SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language';""")
				lang_id = cur.fetchone()['settings_value']

				# from language_settings get short_name
				cur.execute("""SELECT uuid, short_name FROM sloth_language_settings""")
				raw_languages = cur.fetchall()
				languages = {lang['uuid']: lang['short_name'] for lang in raw_languages}
				# from post_types get slugs
				cur.execute("""SELECT uuid, slug FROM sloth_post_types""")
				raw_post_types = cur.fetchall()
				post_types = {pt['uuid']: pt['slug'] for pt in raw_post_types}
				# from posts get slugs, post_type, language
				cur.execute("""SELECT slug, post_type, lang FROM sloth_posts WHERE post_status = 'published'""")
				posts = cur.fetchall()
				urls = [
					Path(os.path.join(
						current_app.config["OUTPUT_PATH"],
						languages[post['lang']] if post['lang'] != lang_id else "",
						post_types[post['post_type']],
						post['slug'],
						"index.html"
					))
					for post in posts
				]
		except Exception as e:
			print(e)
			traceback.print_exc()

		connection.close()

		if urls:
			urls_to_check = [str(url) for url in urls if not url.is_file()]
			response = make_response(json.dumps(
				{"urls": urls_to_check}
			))
			code = 200
		else:
			response = make_response(json.dumps(
				{"urls": []}
			))
			code = 500

	response.headers['Content-Type'] = 'application/json'
	return response, code
