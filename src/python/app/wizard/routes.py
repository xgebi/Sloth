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
        "display_name": request.values["display_name"],
        "password": request.values["password"],
        "email": request.values["email"],
        "sitename": request.values["sitename"]
        }

    con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")

    cur = con.cursor()

    cur.execute(
            sql.SQL("SELECT * FROM sloth_users WHERE username = \"{}\"")
               .format(sql.Identifier(filled.username))
        )
    items = cur.fetchall()

    if (len(items) == 0):        
        user = {
            "uuid": uuid.uuid4(),
            "username": filled.username,
            "display_name": filled.display_name,
            "password": "", # TODO deal with hashing
            "email": filled.email 
        }
        cur.execute(
            sql.SQL("INSERT INTO sloth_users(uuid, username, display_name, password, email) VALUES ()")
               .format(sql.Identifier(filled.username))
        )
        cur.execute(
            sql.SQL("SELECT * FROM sloth_users WHERE username = \"{}\"")
               .format(sql.Identifier(filled.sitename))
        )
        con.commit()

    cur.close()
    con.close()

    return render_template("initial_step.html", filled=filled)

@wiz.route("/registered", methods=["GET"])
def registered():
    return ""