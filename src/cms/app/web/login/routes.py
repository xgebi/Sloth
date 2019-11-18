from flask import request, flash, url_for, current_app, abort, redirect, make_response
from toes.toes import render_toe
from authlib.jose import jwt

from app.authorization.user import User

from app.web.login import login

@login.route("/login")
def show_login():
	return render_toe(template="login.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data={ "page_title": "SlothCMS login" })

@login.route("/login/error")
def show_login_error():
	return render_toe(template="login.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data={ "error": True, "page_title": "SlothCMS login" })


@login.route('/login/process', methods=["POST"])
def process_login(*args, connection=None, **kwargs):
	# get credentials
	username = request.form.get("username")
	password = request.form.get("password")
	if (len(username) == 0 or len(password) == 0):
		return redirect("/login/error")
	# compare credentials with database
	user = User()
	info = user.login_user(username, password)
	"""
	{'uuid': '3238ae5a-b4cc-4a6e-be54-5f64fea77aa5', 'displayName': 'brooke', 'token': '0599e52d-ce0d-46a2-bf95-c43d04c6c3c5', 'expiryTime': 1574033596780.6345, 'permissionsLevel': 1}
	"""
	# if good redirect to dashboard
	if info is not None:		
		response = make_response(redirect('/dashboard'))
		response.set_cookie('sloth_session', info["displayName"]+":"+info["uuid"]+":"+info["token"])
		return response
	return redirect("/login/error")

@login.route("/logout")
def logout():
	cookie = request.cookies.get('sloth_session')
	if cookie is not None and len(cookie.split(":")) == 3:
		cookie = cookie.split(":")
		user = User(cookie[1], cookie[2])
		user.logout_user()
		
	response = make_response(redirect('/login'))
	response.set_cookie('sloth_session', "")
	return response