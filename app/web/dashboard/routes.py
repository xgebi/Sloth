from flask import request, flash, url_for, current_app, abort, redirect, render_template
from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web
from app.posts.post_types import PostTypes
from app.utilities.db_connection import db_connection
import psycopg2
from psycopg2 import sql
import datetime
import traceback

from app.web.dashboard import dashboard


@dashboard.route('/dashboard')
@authorize_web(0)
@db_connection
def show_dashboard(*args, permission_level, connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    cur = connection.cursor()
    raw_recent_posts = []
    raw_upcoming_posts = []
    raw_drafts = []
    raw_messages = []

    try:
        cur.execute(
            sql.SQL(
                """SELECT A.uuid, A.title, A.publish_date, B.display_name 
                FROM sloth_posts AS A INNER JOIN sloth_post_types AS B ON B.uuid = A.post_type 
                WHERE post_status = %s ORDER BY A.publish_date DESC LIMIT 10;"""),
            ['published']
        )
        raw_recent_posts = cur.fetchall()

        cur.execute(
            sql.SQL("""SELECT uuid, title, publish_date, post_type FROM sloth_posts 
                        WHERE post_status = %s ORDER BY publish_date ASC LIMIT 10"""),
            ['scheduled']
        )
        raw_upcoming_posts = cur.fetchall()

        cur.execute(
            sql.SQL("""SELECT uuid, title, publish_date, post_type FROM sloth_posts 
                        WHERE post_status = %s ORDER BY update_date DESC  LIMIT 10"""),
            ['draft']
        )
        raw_drafts = cur.fetchall()

        cur.execute(
            sql.SQL(
                """SELECT uuid, name, sent_date, status 
                FROM sloth_messages WHERE status != 'deleted' ORDER BY sent_date DESC LIMIT 10""")
        )
        raw_messages = cur.fetchall()

    except Exception as e:
        print(traceback.format_exc())
        abort(500)
        cur.close()
        connection.close()

    cur.close()
    connection.close()

    recent_posts = []
    upcoming_posts = []
    drafts = []
    messages = []

    for post in raw_recent_posts:
        recent_posts.append({
            "uuid": post[0],
            "title": post[1],
            "publish_date": datetime.datetime.fromtimestamp(float(post[2]) / 1000.0).strftime("%Y-%m-%d %H:%M"),
            "post_type": post[3]
        })

    for post in raw_upcoming_posts:
        upcoming_posts.append({
            "uuid": post[0],
            "title": post[1],
            "publish_date": datetime.datetime.fromtimestamp(float(post[2]) / 1000.0).strftime("%Y-%m-%d %H:%M"),
            "post_type": post[3]
        })

    for post in raw_drafts:
        drafts.append({
            "uuid": post[0],
            "title": post[1],
            "publish_date": datetime.datetime.fromtimestamp(float(post[2]) / 1000.0).strftime("%Y-%m-%d %H:%M"),
            "post_type": post[3]
        })

    for msg in raw_messages:
        messages.append({
            "uuid": msg[0],
            "name": msg[1],
            "sent_date": datetime.datetime.fromtimestamp(float(msg[2]) / 1000.0).strftime("%Y-%m-%d %H:%M"),
            "status": msg[3]
        })

    return render_template(
        "dashboard.html",
        post_types=post_types_result,
        permission_level=permission_level,
        messages=messages,
        recent_posts=recent_posts,
        drafts=drafts,
        upcoming_posts=upcoming_posts
    )
