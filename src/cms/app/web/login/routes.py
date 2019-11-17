from flask import request, flash, url_for, current_app, abort, redirect
from toes.toes import render_toe

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
	# if good redirect to dashboard
	if info is not None:		
		return redirect("/dashboard")
	return redirect("/login/error")