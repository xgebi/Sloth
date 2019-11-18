from flask import request, flash, url_for, current_app, abort
import json
import psycopg2
from psycopg2 import sql, errors
import uuid

from app.utilities.db_connection import db_connection
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize_rest

from app.api.posts.post_types import post_types as post_types


@post_types.route("/api/post-type-information")
@authorize_rest(0)
@db_connection
def show_post_type_information(*args, connection=None, **kwargs):
	if connection is None:
		abort(500)

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)

	return json.dumps({
		"postTypes": postTypesResult
	})

@post_types.route("/api/post-type/<post_type_id>/detail")
@authorize_rest(1)
@db_connection
def show_post_type_detail(*args, post_type_id, connection=None, **kwargs):
	if connection is None:
		abort(500)

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)
	postTypeDetail = postTypes.get_post_type(connection, post_type_id)

	return json.dumps({
		"postTypes": postTypesResult,
		"postTypeDetail": postTypeDetail
	})