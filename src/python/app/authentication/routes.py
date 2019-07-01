from flask import render_template, request, flash, redirect, url_for, current_app
import psycopg2
from psycopg2 import sql
import bcrypt
import json

from app.authentication import authentication
from app.authorization.user import User

@authentication.route("/login", methods=["GET","POST"])
def login():
    if (request.method == "POST"):
        filled = {}
        filled['username'] = request.form.get('username')
        filled["password"] = request.form.get("password")

        if (filled['username'] == None or filled['password'] == None):
            return render_template("login.html", error="Username or password are incorrect")

        user = User()

        if user.login_user(filled["username"], filled["password"]):
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Username or password are incorrect")

    return render_template("login.html")

def authorization():
    return False