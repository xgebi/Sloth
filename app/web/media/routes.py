from flask import request, flash, url_for, current_app, abort, redirect, render_template
from app.utilities.db_connection import db_connection
from app.utilities import get_default_language
from app.authorization.authorize import authorize_web
from app.post.post_types import PostTypes
import psycopg2
from psycopg2 import sql
import datetime
import uuid

from app.api.media.routes import get_media

from app.web.media import media


@media.route("/media")
@authorize_web(0)
@db_connection
def show_posts_list(*args, permission_level, connection, **kwargs):
    if connection is None:
        return redirect("/database-error")

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    media_data = get_media(connection=connection)
    current_lang = get_default_language(connection=connection)
    connection.close()

    return render_template(
        "media.html",
        post_types=post_types_result,
        permission_level=permission_level,
        media=media_data,
        current_lang=current_lang
    )
