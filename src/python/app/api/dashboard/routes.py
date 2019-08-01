from flask import render_template, request, flash, redirect, url_for, current_app, abort

from pathlib import Path
import json
import os

import psycopg2
import uuid
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize
from app.utilities.db_connection import db_connection

from app.api.dashboard import dashboard
from app.posts.post_types import PostTypes

@dashboard.route("/api/dashboard-information")
@authorize(0)
@db_connection
def dashboard_information(*args, connection=None, **kwargs):
	if connection is None:
		abort(500)

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)

	connection.close()
	return json.dumps({ "postTypes": postTypesResult })