from flask import request, flash, url_for, current_app, abort, redirect, render_template
from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web
from app.posts.post_types import PostTypes
from app.utilities.db_connection import db_connection

from app.web.dashboard import dashboard

@dashboard.route('/dashboard')
@authorize_web(0)
@db_connection
def show_dashboard(*args, permission_level, connection,**kwargs):
   postTypes = PostTypes()
   postTypesResult = postTypes.get_post_type_list(connection)
   # Todo get list of recent posts
   # Todo get list of drafts
   # Todo get messages
   return render_template("dashboard.html", post_types=postTypesResult, permission_level=permission_level)