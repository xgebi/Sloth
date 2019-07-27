from flask import render_template, request, flash, redirect, url_for, current_app, abort
import psycopg2
import uuid

from app.administration.posts import posts
from app.authorization.user import User
from app.administration.posts.post_types import PostTypes

# Posts
@posts.route("/post_type/<post_type_uuid>")
def redirect_to_list(post_type_uuid):
	return redirect(f"/post_type/{post_type_uuid}/list")

@posts.route("/post_type/<post_type_uuid>/list")
def list_posts(post_type_uuid):
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
				[post_type_uuid]
			)
			raw_items = cur.fetchall()
		except Exception as e:
			print(e)
			abort(500)


		cur.close()
		con.close()
		
		return render_template("list.html", post_types = post_types, posts = raw_items, post_type = post_type_uuid)
	
	return redirect("/login")

@posts.route("/post_type/<post_type_uuid>/save/<post_uuid>", methods = ["POST", "PUT"])
def add_post_screen(post_type_uuid, post_uuid):
	return render_template("new_post.html")

@posts.route("/post_type/<post_type_uuid>/add")
def create_new_post(post_type_uuid):
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

		return render_template("post.html", post_types = post_types, post = [ str(uuid.uuid4()) ], post_type = post_type_uuid)
	
	return redirect("/login")

@posts.route("/post_type/<post_type_uuid>/edit/<post_uuid>")
def edit_post(post_type_uuid, post_uuid):
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
				"SELECT uuid, slug, post_type, title, content, css_file, js_file, publish_date, update_date, post_status, tags, categories FROM sloth_posts WHERE uuid = %s AND post_type = %s",
				[post_uuid, post_type_uuid]
			)
			raw_items = cur.fetchone()
		except Exception as e:
			print(e)
			abort(500)


		cur.close()
		con.close()
		
		return render_template("post.html", post_types = post_types, post = raw_items, post_type = post_type_uuid)
	
	return redirect("/login")

# Post types
@posts.route("/post_types")
def redirect_to_post_type_list():
	return redirect(f"/post_types/list")

@posts.route("/post_types/list")
def list_all_post_types():
	pass

@posts.route("/post_types/<post_type_uuid>")
def show_post_type_details(post_type_uuid):
	pass

@posts.route("/post_types/<post_type_uuid>/save")
def save_post_type_details(post_type_uuid):
	pass

@posts.route("/post_types/<post_type_uuid>/categories")
def show_post_type_categories(post_type_uuid):
	pass

@posts.route("/post_types/<post_type_uuid>/categories/save")
def save_post_type_categories(post_type_uuid):
	pass

@posts.route("/post_types/<post_type_uuid>/tags")
def show_post_type_tags(post_type_uuid):
	pass

@posts.route("/post_types/<post_type_uuid>/tags/save")
def save_post_type_tags(post_type_uuid):
	pass