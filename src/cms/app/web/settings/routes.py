from flask import request, flash, url_for, current_app, abort, redirect

from toes.toes import render_toe

from app.web.settings import settings

@settings.route("/settings")
# do something about security!!!
def show_settings():
	settings = {}

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

	return render_toe(template="settings.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data=settings)
