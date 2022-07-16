import os
import psycopg

from app.authorization.authorize import authorize_web
from app.back_office.post.post_types import PostTypes
from app.lists import lists
from app.toes.hooks import Hooks
from app.toes.toes import render_toe_from_path
from app.utilities.db_connection import db_connection
from app.utilities.utilities import get_default_language


@lists.route("/lists")
@authorize_web(0)
@db_connection
def no_post(*args, permission_level: int, connection: psycopg.Connection, **kwargs):

	post_types = PostTypes()
	post_types_result = post_types.get_post_type_list(connection)
	default_language = get_default_language(connection=connection)

	return render_toe_from_path(
		path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
		template="lists.toe.html",
		data={
			"title": "Settings",
			"post_types": post_types_result,
			"permission_level": permission_level,
			"default_lang": default_language,
		},
		hooks=Hooks()
	)