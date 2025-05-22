from flask import request, redirect, make_response, current_app, abort
from app.authorization.authorize import authorize_rest, authorize_web
from app.authorization.user import User, UserInfo
from app.toes.toes import render_toe_from_path
from app.toes.hooks import Hooks
import json
import os
from typing import Tuple
import time
import uuid
import psycopg

from app.routes.login import login
from app.utilities.db_connection import db_connection


@login.route("/login")
def show_login():
	"""
	Renders login page

	:return:
	"""
	return render_toe_from_path(
		path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
		template="login.toe.html",
		data={
			"title": "Log in",
			"status": {},
			"redirect": request.args.get("redirect"),
		},
		hooks=Hooks()
	)


@login.route("/login/error")
def show_login_error():
	"""
	Renders login page with error message

	:return:
	"""
	return render_toe_from_path(
		path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
		template="login.toe.html",
		data={
			"title": "Log in",
			"status": {
				"error": True
			},
			"redirect": request.args.get("redirect")
		},
		hooks=Hooks()
	)


@login.route('/login/process', methods=["POST"])
@db_connection
def process_login(*args, connection: psycopg.Connection, **kwargs):
	"""
	Processes logging in

	:param args:
	:param connection:
	:param kwargs:
	:return:
	"""
	if request.headers.getlist("X-Forwarded-For"):
		ip = request.headers.getlist("X-Forwarded-For")[0]
	else:
		ip = request.remote_addr

	with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
		cur.execute("""
        SELECT ip, banned_until, attempts, time_period FROM sloth_ban_list 
        WHERE ip = %s;""",
					(ip,)
					)
		banned = cur.fetchone()
		if banned is not None:
			if banned["banned_until"] > time.time() * 1000:
				return redirect("/login/error")
		else:
			banned = {
				"ip": ip,
				"banned_until": time.time() * 1000,
				"attempts": 0,
				"time_period": 0,
			}

	# get credentials
	username = request.form.get("username")
	password = request.form.get("password")
	if len(username) == 0 or len(password) == 0:
		return redirect("/login/error")
	# compare credentials with database
	user = User()
	info: UserInfo = user.login_user(username, password)

	# if good redirect to dashboard
	if info is not None:
		with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
			cur.execute("""DELETE FROM sloth_ban_list WHERE ip = %s""", (ip,))
			connection.commit()
			cur.execute("""SELECT settings_value FROM sloth_settings WHERE settings_name = %s;""", ("api_url",))
			host = cur.fetchone()['settings_value']

		if request.args.get("redirect"):
			if current_app.url_map.bind(host).test(request.args.get("redirect")):
				response = make_response(redirect(request.args.get("redirect")))
			else:
				response = make_response(redirect("/"))
		else:
			response = make_response(redirect('/dashboard'))
		response.set_cookie(
			key='sloth_session',
			value=f"{info.display_name}:{info.uuid}:{info.token}",
			secure=True,
			samesite='Strict'
		)
		return response
	else:
		banned["attempts"] += 1
		if banned["attempts"] < 5:
			banned["time_period"] = 0
		elif banned["attempts"] < 10:
			banned["time_period"] = 5 * 60 * 1000
		else:
			banned["time_period"] = 24 * 60 * 60 * 1000
		banned["banned_until"] = (time.time() * 1000) + banned["time_period"]
		with connection.cursor() as cur:
			if banned["attempts"] > 1:
				cur.execute("""UPDATE sloth_ban_list SET attempts = %s, time_period = %s, banned_until = %s,
                last_attempt = %s 
                WHERE ip = %s;""",
							(banned["attempts"], banned["time_period"], banned["banned_until"], time.time() * 1000,
							 banned["ip"]))
			else:
				cur.execute("""INSERT INTO sloth_ban_list (uuid, ip, attempts, last_attempt, banned_until, time_period) 
                VALUES (%s, %s, %s, %s, %s, %s)""",
							(str(uuid.uuid4()), banned["ip"], banned["attempts"], time.time() * 1000,
							 banned["banned_until"], banned["time_period"])
							)
			connection.commit()
	connection.close()
	return redirect("/login/error")


@login.route("/logout")
@authorize_web(0)
def logout(*args, permission_level: int, **kwargs):
	"""
	Processes log out

	:param args:
	:param permission_level:
	:param kwargs:
	:return:
	"""
	cookie = request.cookies.get('sloth_session')
	user = User(cookie[1], cookie[2])
	user.logout_user()

	response = make_response(redirect('/login'))
	response.set_cookie('sloth_session', "")
	return response


@login.route("/api/user/keep-logged-in", methods=["POST"])
@authorize_rest(0)
def keep_logged_in(*args, permission_level, **kwargs):
	"""
	API endpoint to keep logged in user logged in
	:param args:
	:param permission_level:
	:param kwargs:
	:return:
	"""
	return json.dumps({"loggedIn": True})


@login.route("/api/login", methods=['POST'])
def api_login() -> Tuple[str, int]:
	"""
	API endpoint that processes logging in
	:return:
	"""
	# get credentials
	data = json.loads(request.data)
	username = data.get("username")
	password = data.get("password")
	if len(username) == 0 or len(password) == 0:
		return json.dumps({"error": "name and password can't empty"}), 401
	# compare credentials with database
	user = User()
	info: UserInfo = user.login_user(username, password)

	# if good redirect to dashboard
	if info is not None:
		return info.to_json_string(), 200
	return json.dumps({"error": "Unable to login"}), 401


@login.route("/api/logout", methods="POST")
@authorize_rest(0)
def api_logout() -> Tuple[str, int]:
	"""
	API endpoint which logs human out

	:return:
	"""
	data = json.loads(request.data)
	username = data.get("username")
	token = data.get("token")
	user = User(username, token)
	user.logout_user()
	return json.dumps({"status": "logged out"}), 200