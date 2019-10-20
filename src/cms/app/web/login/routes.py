from flask import render_template, request, flash, url_for, current_app, abort, redirect

from app.authorization.user import User

from app.web.login import login

@login.route("/login")
def show_login():
	return render_template('login.html')

@login.route("/login/error")
def show_login_error():
	return render_template('login.html', error=True)


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