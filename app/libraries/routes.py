from app.authorization.authorize import authorize_web
from app.utilities.db_connection import db_connection
from app.toes.hooks import Hooks
from app.toes.toes import render_toe_from_path
from app.post.post_types import PostTypes
from app.utilities import get_default_language
import os

from app.libraries import libraries

# display libraries
@libraries.route("/libraries")
@authorize_web(0)
@db_connection
def show_libraries(*args, permission_level, connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    default_language = get_default_language(connection=connection)

    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="dashboard.toe.html",
        data={
            "title": "Dashboard",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "default_lang": default_language
        },
        hooks=Hooks()
    )


# add library
@libraries.route("/libraries/new", methods=["POST"])
@authorize_web(0)
@db_connection
def add_libraries(*args, permission_level, connection, **kwargs):
    pass


# delete library
@libraries.route("/libraries/delete", methods=["DELETE"])
@authorize_web(0)
@db_connection
def delete_library(*args, permission_level, connection, **kwargs):
    pass
