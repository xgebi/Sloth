from flask import render_template, request, flash, redirect, url_for, current_app
import psycopg2

from app.entry import entry as ep

@ep.route("/", methods=["GET"])
def entry_point():
    config = current_app.config
    
    con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")

    cur = con.cursor()

    cur.execute("SELECT * FROM sloth_users")
    items = cur.fetchall()

    print(items)

    cur.close()
    con.close()

    if (len(items) == 0):
        return redirect("/register", code=302)

    return render_template("spa.html")