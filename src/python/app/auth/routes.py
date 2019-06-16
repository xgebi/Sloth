from flask import render_template, request, flash, redirect, url_for, current_app
import psycopg2
from psycopg2 import sql
import bcrypt
import json

from app.auth import auth

@auth.route("/login", methods=["GET","POST"])
def login():
    if (request.method == "POST"):
        filled = {}
        filled['username'] = request.form.get('username')
        filled["password"] = request.form.get("password")

        if (filled['username'] == None or filled['password'] == None):
            return render_template("login.html", error="Username or password are incorrect")

        config = current_app.config
        con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")
        cur = con.cursor()

        try:
            cur.execute(
                sql.SQL("SELECT password FROM sloth_users WHERE username = '{0}'")
                .format(sql.Identifier(filled['username']))
            )
            items = cur.fetchone()
        except e:
            return render_template("login.html", error="Problem with connecting to the database")
        
        items = items[0][1:-1]
        if bcrypt.checkpw(filled["password"].encode('utf8'), items.encode('utf8')):
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Username or password are incorrect")

    return render_template("login.html")

def authorization():
    return False