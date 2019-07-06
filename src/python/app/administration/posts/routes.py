from flask import render_template, request, flash, redirect, url_for, current_app

from app.administration.posts import posts

@posts.route("/post_type/<uuid>")
def redirect_to_list(uuid):
	return redirect(f"/post_type/{uuid}/list")

@posts.route("/post_type/<uuid>/list")
def list_posts(uuid):
	return render_template("list.html")

@posts.route("/post_type/<uuid>/add")
def add_post(uuid):
	return render_template("new_post.html")