from flask import make_response, abort
import json
from app.post.post_types import PostTypes
from app.authorization.authorize import authorize_rest
from app.utilities.db_connection import db_connection

from app.api.sloth_settings import sloth_settings


@sloth_settings.route("/api/settings", methods=["GET"])
@authorize_rest(1)
@db_connection
def show_settings(*args, connection=None, **kwargs):
	if connection is None:
		abort(500)

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)

	cur = connection.cursor()

	try:		
		cur.execute(
			"SELECT settings_name, display_name, settings_value, settings_value_type FROM sloth_settings WHERE settings_type = 'sloth'"
		)
		raw_items = cur.fetchall()
	except Exception as e:
		print("db error b")
		response = make_response(json.dumps({"error": True}))
		response.headers['Content-Type'] = 'application/json'
		code = 500

		return response, code

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

	response = make_response(json.dumps({ "postTypes": postTypesResult, "settings": items }))
	response.headers['Content-Type'] = 'application/json'
	code = 200

	return response, code
