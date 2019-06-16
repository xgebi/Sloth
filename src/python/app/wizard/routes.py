from flask import render_template, request, flash, redirect, url_for, current_app
import psycopg2
import uuid

from app.wizard import wizard as wiz

@wiz.route("/register", methods=["GET"])
def wizard():
    filled = {}
    return render_template("initial_step.html", filled=filled)

@wiz.route("/process-registration", methods=["POST"])
def registration_processing():
    config = current_app.config

    filled = {
        "username": request.values["username"],
        "password": request.values["password"],
        "email": request.values["email"],
        "sitename": request.values["sitename"]
        }

    con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")

    cur = con.cursor()

    cur.execute("SELECT * FROM sloth_users")
    items = cur.fetchall()

    print(items)

    cur.close()
    con.close()

    return render_template("initial_step.html", filled=filled)

@wiz.route("/registered", methods=["GET"])
def registered():
    return ""