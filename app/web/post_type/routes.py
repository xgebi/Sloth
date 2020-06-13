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
@authorize_web(0)
@db_connection
def show_post_types(*args, permission_level, connection, **kwargs):
    if connection is None:
        return redirect("/database-error")

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    return render_template("post-types-list.html", post_types=post_types_result, permission_level=permission_level)
