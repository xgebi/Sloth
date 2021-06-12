import json

from app.post.post_types import PostTypes
from app.toes.toes import render_toe_from_path
from flask import abort, make_response, request
from datetime import datetime, timedelta, date
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
        first_day = (datetime.today() - timedelta(days=6, hours=datetime.today().hour, minutes=datetime.today().minute,seconds=datetime.today().second, microseconds=datetime.today().microsecond))
        seven_days_time_stamp = first_day.timestamp() * 1000
        cur.execute(
            sql.SQL(
                """SELECT uuid, pathname, last_visit, browser, browser_version 
                FROM sloth_analytics WHERE last_visit > %s ORDER BY last_visit DESC"""
            ),
            (seven_days_time_stamp, )
        )
        temp_last_seven_days = [{
            "uuid": item[0],
            "pathname": item[1],
            "lastVisit": item[2],
            "browser": item[3],
            "browserVersion": item[4],
        } for item in cur.fetchall()]

        cur.execute(
            sql.SQL(
                """
                SELECT pathname, count(uuid) 
                FROM sloth_analytics 
                GROUP BY pathname 
                ORDER BY count(uuid) DESC"""
            )
        )
        most_visited = json.dumps([{
            "pathname": item[0],
            "count": item[1]
        } for item in cur.fetchall()])
    except Exception as e:
        print(traceback.format_exc())
        abort(500)
        cur.close()
        connection.close()

    cur.close()
    default_language = get_default_language(connection=connection)
    connection.close()

    last_seven_days = {(first_day + timedelta(days=i)).strftime("%Y-%m-%d"): 0 for i in range(7)}
    for item in temp_last_seven_days:
        # parse date to date
        visit_date = date.fromtimestamp(item["lastVisit"] / 1000).isoformat()
        if visit_date in last_seven_days:
            last_seven_days[visit_date] += 1

    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="analytics-dashboard.toe.html",
        data={
            "title": "Analytics",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "default_lang": default_language,
            "last_seven_days": json.dumps(last_seven_days),
            "most_visited": most_visited
        },
        hooks=Hooks()
    )
