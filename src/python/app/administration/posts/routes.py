from flask import render_template, request, flash, redirect, url_for, current_app

from app.administration.posts import posts

@posts.route("/post_type/<uuid>")
def redirect_to_list(uuid):
	return redirect(f"/post_type/{uuid}/list")

@posts.route("/post_type/<uuid>/list")
def list_posts(uuid):
	return render_template("list.html")

@posts.route("/post_type/<uuid>/add")
def add_post_screen(uuid):
	return render_template("new_post.html")

@posts.route("/post_type/<uuid>/create")
def create_new_post(uuid):
	pass

@posts.route("/post_types")
def redirect_to_post_type_list(uuid):
	return redirect(f"/post_types/{uuid}/list")

@posts.route("/post_types/list")
def list_all_post_types(uuid):
	pass

@posts.route("/post_types/<uuid>")
def show_post_type_details(uuid):
	pass

@posts.route("/post_types/<uuid>/categories")
def show_post_type_categories(uuid):
	pass

@posts.route("/post_types/<uuid>/tags")
def show_post_type_tags(uuid):
	pass