from flask import render_template
import os
from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web
from app.toes.hooks import Hooks
from app.post.post_types import PostTypes
from app.toes.toes import render_toe_from_path
from app.settings.content import content


@content.route("/settings/import")
@authorize_web(1)
@db_connection
def show_import_settings(*args, permission_level, connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    # Import posts
    return render_toe_from_path(
        template="import-data.toe.html",
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        data={
            "title": "Import posts",
            "post_types": post_types_result,
            "permission_level": permission_level
        },
        hooks=Hooks()
    )


@content.route("/settings/export")
@authorize_web(1)
@db_connection
def show_export_settings(*args, permission_level, connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    # Import posts
    return render_toe_from_path(
        template="export-data.toe.html",
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        data={
            "title": "Import posts",
            "post_types": post_types_result,
            "permission_level": permission_level
        },
        hooks=Hooks()
    )
