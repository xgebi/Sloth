from flask import request, abort, redirect, render_template
from psycopg2 import sql
import json
from app.post.post_types import PostTypes
from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web, authorize_rest

from app.mock_endpoints import mock_endpoints


@mock_endpoints.route("/mock-endpoints")
@authorize_web(0)
@db_connection
def show_endpoints_list(*args, permission_level, connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    return render_template("mock-endpoints-list.html", post_types=post_types_result, permission_level=permission_level
                           )


@mock_endpoints.route("/mock-endpoints/<endpoint>", methods=["GET"])
@authorize_web(0)
@db_connection
def show_endpoint(*args, permission_level, connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    return render_template("mock-endpoint.html", post_types=post_types_result, permission_level=permission_level
                           )


@mock_endpoints.route("/mock-endpoints/new", methods=["GET"])
@authorize_web(0)
@db_connection
def show_endpoint(*args, permission_level, connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    return render_template("mock-endpoint.html", post_types=post_types_result, permission_level=permission_level
                           )


@mock_endpoints.route("/mock-endpoints", methods=["POST", "PUT"])
@authorize_web(0)
@db_connection
def save_endpoint(*args, permission_level, connection, **kwargs):
    pass