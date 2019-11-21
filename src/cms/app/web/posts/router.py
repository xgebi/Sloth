from flask import request, flash, url_for, current_app, abort, redirect
from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web

from app.web.posts import posts

@root.route("/posts/<post_type>")
@authorize_web(0)
@db_connection
def show_posts_list():
	if connection is None:
		return render_toe(template="settings.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data={ "error": "No connection to database" })
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

	return render_toe(template="design.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data={ "page_title": "Sloth - Design System", "design_system": True, "test": "<br /> Hello" } )
