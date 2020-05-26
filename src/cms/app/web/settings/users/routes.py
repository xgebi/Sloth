from flask import request, flash, url_for, current_app, abort, redirect, render_template
import psycopg2
from psycopg2 import sql

import app
import os
from pathlib import Path
import bcrypt
import json

from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web

from app.posts.post_types import PostTypes

from app.web.settings.users import settings_users

@settings_users.route("/settings/users")
@authorize_web(1)
@db_connection
def show_users_list(*args, permission_level, connection, **kwargs):
	if connection is None:
		return redirect("/database-error")	

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)
	
	config = current_app.config

	cur = connection.cursor()

	raw_users = []
	try:		
		cur.execute(
			"SELECT uuid, username, display_name FROM sloth_users"
		)
		raw_users = cur.fetchall()
	except Exception as e:
		print("db error")
		abort(500)

	cur.close()
	connection.close()

	user_list = []
	for user in raw_users:
		user_list.append({
			"uuid": user[0],
			"username": user[1],
			"display_name": user[2]
		})

	return render_template("users-list.html", post_types=postTypesResult, permission_level=permission_level, user_list=user_list)

@settings_users.route("/settings/users/<user>")
@authorize_web(0)
@db_connection
def show_user(*args, permission_level, connection=None, user, **kwargs):
	token = request.cookies.get('sloth_session').split(":")

	if (permission_level == 0 and token[1] != user):
		return redirect("/unauthorized")

	if connection is None:
		return redirect("/database-error")		

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)
	
	config = current_app.config

	cur = connection.cursor()

	raw_users = []
	try:		
		cur.execute(
			sql.SQL("SELECT uuid, username, display_name, email, permissions_level FROM sloth_users WHERE user = %s"),
			[token[1]]
		)
		raw_user = cur.fetchone()
	except Exception as e:
		print("db error")
		abort(500)

	cur.close()
	connection.close()

	user = {
		"uuid": raw_user[0],
		"username": raw_user[1],
		"display_name": raw_user[2],
		"email": raw_user[3],
		"permissions_level": raw_user[4]
	}

	return render_template("user.html", ost_types=postTypesResult, permission_level=permission_level, user=user)

@settings_users.route("/settings/users/<user>/save")
@authorize_web(0)
@db_connection
def save_user(*args, user, connection=None, **kwargs):
	pass