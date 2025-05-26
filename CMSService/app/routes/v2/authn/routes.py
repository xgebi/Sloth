from flask import request, redirect, make_response, current_app, abort
from app.authorization.authorize import authorize_rest, authorize_web
from app.authorization.user import User, UserInfo
import json
from typing import Tuple

from app.routes.v2.authn import authn

@authn.route("/api/v2/check-in", methods=["POST"])
@authorize_rest(0)
def keep_logged_in(*args, permission_level, **kwargs):
	"""
	API endpoint to keep logged in user logged in
	:param args:
	:param permission_level:
	:param kwargs:
	:return:
	"""
	return json.dumps({"status": True})


@authn.route("/api/v2/login", methods=['POST'])
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


@authn.route("/api/v2/logout", methods=["POST"])
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
	return json.dumps({"status": False}), 200