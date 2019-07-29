from flask import render_template, request, flash, redirect, url_for, current_app, abort

from pathlib import Path
import json
import os

import psycopg2
import uuid
from app.authorization.user import User
from app.posts.post_types import PostTypes

from app.api.dashboard import dashboard

@dashboard.route("/api/dashboard-information")
def dashboard_information():
	PERMISSION_LEVEL = 0

	auth = request.headers.get('authorization').split(":")
	user = User(auth[0], auth[1])
	if (user.authorize_user(PERMISSION_LEVEL)):
		config = current_app.config
		con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")

		postTypes = PostTypes()
		postTypesResult = postTypes.get_post_type_list(con)

		con.close()
		return json.dumps({ "postTypes": postTypesResult })
	return json.dumps({ "dashboard": "Error" }), 403
