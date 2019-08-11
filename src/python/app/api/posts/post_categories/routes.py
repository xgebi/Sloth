from flask import render_template, request, flash, redirect, url_for, current_app
from app.api.posts.post_categories import post_categories as post_categories

from app.utilities.db_connection import db_connection
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize

@post_categories.route("/api/posts/<post_id>/categories-information")
@authorize(0)
@db_connection
def show_categories_list(*args, post_id, connection=None, **kwargs):
	if connection is None:
		abort(500)

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)