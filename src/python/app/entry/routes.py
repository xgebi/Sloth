from flask import render_template, request, flash, redirect, url_for, current_app
import psycopg2
from psycopg2 import sql
import time

from app.entry import entry as ep

@ep.route("/", methods=["GET"])
def entry_point():
	config = current_app.config
	
	con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")

	cur = con.cursor()
	items = []
	try:
		cur.execute("SELECT * FROM sloth_users")
		items = cur.fetchall()
	except Exception as e:
		return redirect("/register", code=302)

	cur.close()
	con.close()

	if (len(items) == 0):
		return redirect("/register", code=302)

	if 'sloth_user' in request.cookies:
		sloth_user = request.cookies.get('sloth_user')
		cur.execute(
			sql.SQL("SELECT * FROM sloth_users WHERE uuid=\"{0}\" AND token=\"{1}\"")
			   .format(sql.Identifier(sloth_user.uuid), sql.Identifier(sloth_user.token))
		)
		items = cur.fetchall()
		cur.close()
		con.close()
		if (len(items) == 0 or items[0].token_expiry_time < time.time()):
			return redirect("/login")

		return render_template("index.html")
	
	cur.close()
	con.close()
	return redirect("/login")