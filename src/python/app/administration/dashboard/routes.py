from flask import render_template, request, flash, redirect, url_for, current_app


from app.administration.dashboard import dashboard
from app.authorization.user import User

@dashboard.route("/dashboard", methods=["GET"])
def dashboard():
    userId = request.cookies.get('userID')
    userToken = request.cookies.get('userToken')
    user = User(userId, userToken)
    if user.authorize_user(0):
        return render_template("dashboard.html")
    return redirect("/login")