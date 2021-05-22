import json

from app.post.post_types import PostTypes
from app.toes.toes import render_toe_from_path
from flask import abort, make_response, request
from datetime import datetime
from app.authorization.authorize import authorize_web
from app.toes.hooks import Hooks
from app.utilities.db_connection import db_connection
from app.utilities import get_default_language
import traceback
import os
from psycopg2 import sql

from app.dashboard.analytics import analytics


@analytics.route('/dashboard/analytics')
@authorize_web(0)
@db_connection
def show_dashboard(*args, permission_level, connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    cur = connection.cursor()

    try:
        cur.execute(
            sql.SQL(
                """SELECT uuid, pathname, last_visit, browser, browser_version 
                FROM sloth_analytics ORDER BY last_visit DESC"""
            )
        )
        data = json.dumps([{
            "uuid": item[0],
            "pathname": item[1],
            "lastVisit": datetime.fromtimestamp(item[2] / 1000),
            "browser": item[3],
            "browserVersion": item[4],
        } for item in cur.fetchall()])
    except Exception as e:
        print(traceback.format_exc())
        abort(500)
        cur.close()
        connection.close()

    cur.close()
    default_language = get_default_language(connection=connection)
    connection.close()

    # TODO process data

    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="analytics-dashboard.toe.html",
        data={
            "title": "Analytics",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "default_lang": default_language,
            "data": data
        },
        hooks=Hooks()
    )
