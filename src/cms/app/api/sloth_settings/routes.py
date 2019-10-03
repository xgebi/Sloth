from flask import render_template, request, flash, url_for, current_app, make_response, abort
import psycopg2
from psycopg2 import sql
import bcrypt
import json
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize
from app.utilities.db_connection import db_connection

from app.api.sloth_settings import sloth_settings

@sloth_settings.route("/api/settings", methods=["GET"])
@authorize(1)
@db_connection
def show_settings(*args, connection=None, **kwargs):
	if connection is None:
		abort(500)

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)

	cur = connection.cursor()

	raw_items = []
	try:		
		cur.execute(
			"SELECT settings_name, display_name, settings_value, settings_value_type FROM sloth_settings WHERE settings_type = 'sloth'"
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
			"settingsName": item[0],
			"displayName": item[1],
			"settingsValue": item[2],
			"settingsValueType": item[3]
		})

	return json.dumps({ "postTypes": postTypesResult, "settings": items })

@sloth_settings.route("/api/settings/save", methods=["PUT", "POST"])
@authorize(1)
@db_connection
def save_settings(*args, connection=None, **kwargs):
	updated_settings = json.loads(request.data);

	cur = connection.cursor()
	raw_items = []
	try:		
		for setting in updated_settings['settings']:
			cur.execute(
				sql.SQL("UPDATE sloth_settings SET settings_value = %s WHERE settings_name = %s"),
				[setting["settingsValue"], setting["settingsName"]]
			)
		connection.commit()

		cur.execute(
			"SELECT settings_name, display_name, settings_value, settings_value_type FROM sloth_settings WHERE settings_type = 'sloth'"
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
			"settingsName": item[0],
			"displayName": item[1],
			"settingsValue": item[2],
			"settingsValueType": item[3]
		})

	return json.dumps({ "settings": items })