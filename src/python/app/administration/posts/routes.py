from flask import render_template, request, flash, redirect, url_for, current_app, abort
import psycopg2

from app.administration.posts import posts
from app.authorization.user import User
from app.administration.posts.post_types import PostTypes

# Posts
@posts.route("/post_type/<uuid>")
def redirect_to_list(uuid):
	return redirect(f"/post_type/{uuid}/list")

@posts.route("/post_type/<uuid>/list")
def list_posts(uuid):
	userId = request.cookies.get('userID')
	userToken = request.cookies.get('userToken')
	user = User(userId, userToken)
	if user.authorize_user(0):
		config = current_app.config
		con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")
		cur = con.cursor()
		post_types = PostTypes.get_post_type_list(None, con)

		try:
			cur.execute(
				"SELECT uuid, title, publish_date, update_date, post_status, tags, categories FROM sloth_posts WHERE post_type = %s",
				[uuid]
			)
			raw_items = cur.fetchall()
		except Exception as e:
			print(e)
			abort(500)


		cur.close()
		con.close()
		
		return render_template("list.html", post_types = post_types, posts = raw_items, post_type = uuid)
	
	return redirect("/login")

@posts.route("/post_type/<uuid>/add")
def add_post_screen(uuid):
	return render_template("new_post.html")

@posts.route("/post_type/<uuid>/create")
def create_new_post(uuid):
	pass

@posts.route("/post_type/<uuid>/edit/<post_uuid>")
def edit_post(uuid, post_uuid):
	return "Hello and bye"

# Post types
@posts.route("/post_types")
def redirect_to_post_type_list(uuid):
	return redirect(f"/post_types/{uuid}/list")

@posts.route("/post_types/list")
def list_all_post_types(uuid):
	pass

@posts.route("/post_types/<uuid>")
def show_post_type_details(uuid):
	pass

@posts.route("/post_types/<uuid>/save")
def save_post_type_details(uuid):
	pass

@posts.route("/post_types/<uuid>/categories")
def show_post_type_categories(uuid):
	pass

@posts.route("/post_types/<uuid>/categories/save")
def save_post_type_categories(uuid):
	pass

@posts.route("/post_types/<uuid>/tags")
def show_post_type_tags(uuid):
	pass

@posts.route("/post_types/<uuid>/tags/save")
def save_post_type_tags(uuid):
	pass