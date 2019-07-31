from flask import render_template, request, flash, redirect, url_for, current_app, make_response, abort
import psycopg2
from psycopg2 import sql
import bcrypt
import json
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize

from app.api.sloth_settings import sloth_settings

@sloth_settings.route("/api/settings", methods=["GET"])
@authorize(1)
def show_settings():
	config = current_app.config
	con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(con)

	cur = con.cursor()

	raw_items = []
	try:		
		cur.execute(
			"SELECT settings_name, display_name, settings_value FROM sloth_settings WHERE section_id = '0'"
		)
		raw_items = cur.fetchall()
	except Exception as e:
		print("db error")
		abort(500)

	cur.close()
	con.close()

	items = []
	for item in raw_items:
		items.append({
			"settingsName": item[0],
			"displayName": item[1],
			"settingsValue": item[2]
		})

	return json.dumps({ "postTypes": postTypesResult, "settings": items })