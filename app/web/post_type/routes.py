from flask import request, flash, url_for, current_app, abort, redirect, render_template
from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web
from app.posts.post_types import PostTypes
import psycopg2
from psycopg2 import sql
import datetime
import uuid

from app.web.post_type import post_type


@post_type.route("/post-types")
@authorize_web(1)
@db_connection
def show_post_types(*args, permission_level, connection, **kwargs):
    if connection is None:
        return redirect("/database-error")

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    return render_template("post-types-list.html", post_types=post_types_result, permission_level=permission_level)


@post_type.route("/post-type/new", methods=["GET"])
@authorize_web(1)
@db_connection
def new_post_type(*args, permission_level, connection, **kwargs):
    if connection is None:
        return redirect("/database-error")

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    type = {
        "uuid": uuid.uuid4()
    }

    return render_template(
        "post-type.html",
        post_types=post_types_result,
        permission_level=permission_level,
        post_type=type,
        new=True
    )


@post_type.route("/post-type/<post_type>", methods=["GET"])
@authorize_web(1)
@db_connection
def show_post_type(*args, permission_level, connection, type, **kwargs):
    if connection is None:
        return redirect("/database-error")

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    post_types.get_post_type(connection, post_type)

    return render_template(
        "post-type.html",
        post_types=post_types_result,
        permission_level=permission_level,
        post_type=type
    )


@post_type.route("/post-type/<post_type>", methods=["POST", "PUT"])
@authorize_web(1)
@db_connection
def save_post_type(*args, permission_level, connection, type, **kwargs):
    if connection is None:
        return redirect("/database-error")

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    post_types.get_post_type(connection, type)

    return render_template(
        "post-type.html",
        post_types=post_types_result,
        permission_level=permission_level,
        post_type=type
    )


@post_type.route("/post-type/<post_type>", methods=["POST", "PUT", "DELETE"])
@authorize_web(1)
@db_connection
def delete_post_type(*args, permission_level, connection, type, **kwargs):
    if connection is None:
        return redirect("/database-error")

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    post_types.get_post_type(connection, type)

    return render_template(
        "post-type.html",
        post_types=post_types_result,
        permission_level=permission_level,
        post_type=type
    )
