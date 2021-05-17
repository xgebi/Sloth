from flask import render_template

from app.authorization.authorize import authorize_web
from app.utilities.db_connection import db_connection
from app.utilities import get_default_language
from app.post.post_types import PostTypes

from app.lists import lists


@lists.route("/lists")
@authorize_web(0)
@db_connection
def no_post(*args, permission_level, connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    default_lang = get_default_language(connection=connection)
    return render_template("lists.html",
                           post_types=post_types_result,
                           permission_level=permission_level,
                           default_lang=default_lang
                           )