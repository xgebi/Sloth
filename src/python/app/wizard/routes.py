from flask import render_template, request, flash, redirect, url_for, current_app
import psycopg2
from psycopg2 import sql
import uuid
import bcrypt

from app.wizard import wizard as wiz

@wiz.route("/register", methods=["GET"])
def wizard():
    filled = {}
    return render_template("initial_step.html", filled=filled)

@wiz.route("/process-registration", methods=["POST"])
def registration_processing():
    config = current_app.config
    filled = {}
    filled['username'] = request.form.get('username')
    filled["display_name"] = request.form.get("display_name")
    filled["password"] = request.form.get("password")
    filled["email"] = request.form.get("email")
    filled["sitename"] = request.form.get("sitename")

    missing = []

    for key,value in filled.items():
        if filled[key] == None:
            missing.append(key)
    
    if (len(missing) == 0):
        filled['password'] = ""
        return render_template("initial_step.html", filled=filled, missing=missing)

    con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")

    cur = con.cursor()

    items = {}

    try:
        cur.execute(
                sql.SQL("SELECT * FROM sloth_users WHERE username = '{}'")
                .format(sql.Identifier(filled['username']))
            )
        items = cur.fetchall()
    except e:
        filled['password'] = ""
        return render_template("initial_step.html", filled=filled, error="Database error")
    
    if (len(items) == 0):        
        user = {}
        user["uuid"] = str(uuid.uuid4())
        user["username"] = filled["username"]
        user["password"] = bcrypt.hashpw(filled["password"].encode("utf-8"), bcrypt.gensalt(rounds=15)).decode("utf-8")
        user["email"] = filled["email"]
        
        try:
            cur.execute(
                sql.SQL("INSERT INTO sloth_users(uuid, username, display_name, password, email) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')")
                .format(sql.Identifier(user["uuid"]),
                        sql.Identifier(user["username"]),
                        sql.Identifier(user["username"]),
                        sql.Identifier(user["password"]),
                        sql.Identifier(user["email"]))
            )
            cur.execute(
                sql.SQL("INSERT INTO sloth_settings VALUES ('sitename', 'Sitename', '{0}', '0', 'parent', 'Settings')")
                .format(sql.Identifier(filled["sitename"]))
            )
            con.commit()
        except e:
            filled['password'] = ""
            return render_template("initial_step.html", filled=filled, error="Database error")

        cur.close()
        con.close()

        return redirect("/registered")
    
    cur.close()
    con.close()
    
    filled['password'] = ""
    return render_template("initial_step.html", filled=filled)

@wiz.route("/registered", methods=["GET"])
def registered():
    return render_template("final_step.html")