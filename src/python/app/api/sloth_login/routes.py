from flask import render_template, request, flash, redirect, url_for, current_app, make_response
import psycopg2
from psycopg2 import sql
import bcrypt
import json

from app.authorization.user import User

from app.api.sloth_login import sloth_login

@sloth_login.route("/api/login", methods=["POST"])
def login():
	filled = json.loads(request.data);

	if (filled['username'] == None or filled['password'] == None):
		return json.dumps({ "error": "Username or password is missing" }), 401

	user = User()
	info = user.login_user(filled["username"], filled["password"])
	
	if info is not None:		
		return json.dumps(info), 200
	else:
		return json.dumps({ "error": "Username or password is incorrect" }), 401
	return json.dumps({ "error": "Server error" }), 500

@sloth_login.route("/api/login-refresh", methods=["POST", "PUT"])
def refresh_login():
	filled = json.loads(request.data);

	user = User()
	updated_info = user.refresh_login(filled)

	if updated_info:
		return json.dumps({ "loggedIn": True }), 200
	return json.dumps({ "error": "Authorization expired" }), 403

@sloth_login.route("/api/logout", methods=["POST", "PUT"])
def logout():
	filled = json.loads(request.data);

	user = User()
	updated_info = user.logout_user(filled)

	if updated_info is not None:
		return json.dumps({ "loggedIn": False }), 200
	return json.dumps({ "error": "Unauthorized" }), 403