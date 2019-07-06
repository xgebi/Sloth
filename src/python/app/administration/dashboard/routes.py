from flask import render_template, request, flash, redirect, url_for, current_app
import psycopg2

from app.administration.dashboard import dashboard
from app.authorization.user import User
from app.posts.post_types import PostTypes

@dashboard.route("/dashboard", methods=["GET"])
def dashboard():
	userId = request.cookies.get('userID')
	userToken = request.cookies.get('userToken')
	user = User(userId, userToken)
	if user.authorize_user(0):
		config = current_app.config
		con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")
		cur = con.cursor()
		post_types = PostTypes.get_post_type_list(None, con)


		cur.close()
		con.close()
		
		return render_template("dashboard.html", post_types = post_types)
	
	return redirect("/login")