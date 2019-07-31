from flask import render_template, request, flash, redirect, url_for, current_app, abort

from pathlib import Path
import json
import os

import psycopg2
import uuid
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize

from app.api.dashboard import dashboard


@dashboard.route("/api/dashboard-information")
@authorize(0)
def dashboard_information():
	config = current_app.config
	con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(con)

	con.close()
	return json.dumps({ "postTypes": postTypesResult })