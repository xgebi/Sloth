from flask import request, redirect, make_response, render_template

from app.authorization.authorize import authorize_rest
from app.authorization.user import User
import json

from app.login import login


@login.route("/login")
def show_login():
    return render_template("login.html", status={"empty": True}, redirect=request.args.get("redirect"))


@login.route("/login/error")
def show_login_error():
    return render_template("login.html", status={"error": True})


@login.route('/login/process', methods=["POST"])
def process_login(*args, connection=None, **kwargs):
    # get credentials
    username = request.form.get("username")
    password = request.form.get("password")
    if len(username) == 0 or len(password) == 0:
        return redirect("/login/error")
    # compare credentials with database
    user = User()
    info = user.login_user(username, password)

    # if good redirect to dashboard
    if info is not None:
        response = make_response(redirect('/dashboard' if request.args.get("redirect") is None else request.args.get("redirect")))
        response.set_cookie('sloth_session', info["display_name"] + ":" + info["uuid"] + ":" + info["token"])
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


@login.route("/api/user/keep-logged-in", methods=["POST"])
@authorize_rest(0)
def keep_logged_in(*args, permission_level, **kwargs):
    return json.dumps({"loggedIn": True})
