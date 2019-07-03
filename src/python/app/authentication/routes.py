from flask import render_template, request, flash, redirect, url_for, current_app, make_response
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
        cookie_info = user.login_user(filled["username"], filled["password"])
        
        if cookie_info is not None:

            resp = make_response(redirect("/dashboard"))
            resp.set_cookie('userID', cookie_info[0])
            resp.set_cookie('userToken', cookie_info[1])
            
            return resp
        else:
            return render_template("login.html", error="Username or password are incorrect")

    return render_template("login.html")

def authorization():
    return False