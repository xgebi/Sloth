from flask import abort, render_template, request, flash, url_for, current_app
from app.authorization.authorize import authorize_web, authorize_rest
from app.utilities.db_connection import db_connection
from app.utilities import get_default_language
import json
import re
from psycopg2 import sql, errors
import datetime
import traceback

import uuid
from time import time

from app.post.post_types import PostTypes

from app.dashboard import dashboard


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
            sql.SQL(
                """SELECT A.uuid, A.title, A.publish_date, B.display_name 
                FROM sloth_posts AS A INNER JOIN sloth_post_types AS B ON B.uuid = A.post_type 
                WHERE post_status = %s ORDER BY A.publish_date ASC LIMIT 10;"""),
            ['scheduled']
        )
        raw_upcoming_posts = cur.fetchall()

        cur.execute(
            sql.SQL(
                """SELECT A.uuid, A.title, A.update_date, B.display_name 
                FROM sloth_posts AS A INNER JOIN sloth_post_types AS B ON B.uuid = A.post_type 
                WHERE post_status = %s ORDER BY A.publish_date DESC LIMIT 10;"""),
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
    default_language = get_default_language(connection=connection)
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
            "publish_date": datetime.datetime.fromtimestamp(float(post[2]) / 1000.0).strftime("%Y-%m-%d %H:%M")
            if post[2] is not None else "",
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
        upcoming_posts=upcoming_posts,
        current_lang=default_language
    )


@dashboard.route("/api/dashboard-information")
@authorize_rest(0)
@db_connection
def dashboard_information(*args, connection=None, **kwargs):
    if connection is None:
        abort(500)

    postTypes = PostTypes()
    postTypesResult = postTypes.get_post_type_list(connection)

    cur = connection.cursor()
    raw_recent_posts = []
    raw_upcoming_posts = []
    raw_drafts = []

    try:
        cur.execute(
            sql.SQL("SELECT uuid, title, publish_date, post_type FROM sloth_posts WHERE post_status = %s LIMIT 10"),
            ['published']
        )
        raw_recent_posts = cur.fetchall()

        cur.execute(
            sql.SQL("SELECT uuid, title, publish_date, post_type FROM sloth_posts WHERE post_status = %s LIMIT 10"),
            ['scheduled']
        )
        raw_upcoming_posts = cur.fetchall()

        cur.execute(
            sql.SQL("SELECT uuid, title, publish_date, post_type FROM sloth_posts WHERE post_status = %s LIMIT 10"),
            ['draft']
        )
        raw_drafts = cur.fetchall()

    except Exception as e:
        print(traceback.format_exc())
        abort(500)

    connection.close()
    return json.dumps({
        "postTypes": postTypesResult,
        "recentPosts": format_post_data(raw_recent_posts),
        "upcomingPosts": format_post_data(raw_upcoming_posts),
        "drafts": format_post_data(raw_drafts)
    })


@dashboard.route("/api/dashboard-information/create-draft", methods=["POST"])
@authorize_rest(0)
@db_connection
def create_draft(*args, connection=None, **kwargs):
    if connection is None:
        abort(500)

    draft = json.loads(request.data)

    slug = re.sub('\s+', '-', draft['title'])
    slug = re.sub('[^0-9a-zA-Z\-]+', '', slug)

    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL(
                """INSERT INTO sloth_posts (uuid, title, slug, content, post_type, post_status, update_date) 
                VALUES (%s, %s, %s, %s, %s, 'draft', %s)"""),
            [str(uuid.uuid4()), draft['title'], slug, draft['text'], draft['postType'], time() * 1000]
        )
        connection.commit()
        cur.execute(
            sql.SQL("SELECT uuid, title, publish_date, post_type FROM sloth_posts WHERE post_status = %s LIMIT 10"),
            ['draft']
        )
        raw_drafts = cur.fetchall()
    except Exception as e:
        print(traceback.format_exc())
        return json.dumps({"error": "Database error"}), 500

    cur.close()
    connection.close()

    return json.dumps({
        "drafts": format_post_data(raw_drafts)
    })


def format_post_data(postArr):
    posts = [];
    for post in postArr:
        posts.append({
            "uuid": post[0],
            "title": post[1],
            "publishDate": post[2],
            "postType": post[3]
        })
    return posts
