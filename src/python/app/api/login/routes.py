from flask import render_template, request, flash, redirect, url_for, current_app, make_response
import psycopg2
from psycopg2 import sql
import bcrypt
import json

from app.authorization.user import User

from app.api.login import login

@login.route("/api/login", methods=["POST"])
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
