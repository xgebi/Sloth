import os

from app.authorization.authorize import authorize_rest, authorize_web
from app.utilities.db_connection import db_connection
from app.utilities import get_default_language, get_languages
from app.post.post_types import PostTypes
from app.toes.toes import render_toe_from_path
from app.toes.hooks import Hooks

from app.settings.localized_settings import localized_settings


@localized_settings.route("/settings/localized-settings")
@authorize_web(1)
@db_connection
def show_localized_settings(*args, permission_level, connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    default_lang = get_default_language(connection=connection)
    languages = get_languages(connection=connection)
    # get home desc, name
    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="localized-settings.toe.html",
        data={
            "title": "Dashboard",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "default_lang": default_lang
        },
        hooks=Hooks()
    )


@localized_settings.route("/settings/localized-settings/save", methods=["POST"])
@authorize_web(1)
@db_connection
def show_localized_settings(*args, permission_level, connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    default_lang = get_default_language(connection=connection)
    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="localized-settings.toe.html",
        data={
            "title": "Dashboard",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "default_lang": default_lang
        },
        hooks=Hooks()
    )
