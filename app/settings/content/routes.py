from flask import render_template

from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web

from app.post.post_types import PostTypes

from app.settings.content import content


@content.route("/settings/import")
@authorize_web(1)
@db_connection
def show_import_settings(*args, permission_level, connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    return render_template("import-data.html", post_types=post_types_result, permission_level=permission_level)
