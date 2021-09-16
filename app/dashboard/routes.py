from flask import abort, make_response, request
from app.authorization.authorize import authorize_web, authorize_rest
from app.toes.hooks import Hooks
from app.utilities.db_connection import db_connection_legacy, db_connection
from app.utilities import get_default_language
import json
import re
from psycopg2 import sql
import datetime
import traceback
import os
import uuid
from time import time
import psycopg

from app.post.post_types import PostTypes
from app.toes.toes import render_toe_from_path
from app.dashboard import dashboard


@dashboard.route('/dashboard')
@authorize_web(permission_level=0)
@db_connection
def show_dashboard(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    with connection.cursor() as cur:
        try:
            cur.execute(
                """SELECT A.uuid, A.title, A.publish_date, B.display_name 
                    FROM sloth_posts AS A INNER JOIN sloth_post_types AS B ON B.uuid = A.post_type 
                    WHERE post_status = %s ORDER BY A.publish_date DESC LIMIT 10;""",
                ('published',)
            )
            raw_recent_posts = cur.fetchall()

            cur.execute(
                """SELECT A.uuid, A.title, A.publish_date, B.display_name 
                    FROM sloth_posts AS A INNER JOIN sloth_post_types AS B ON B.uuid = A.post_type 
                    WHERE post_status = %s ORDER BY A.publish_date LIMIT 10;""",
                ('scheduled',)
            )
            raw_upcoming_posts = cur.fetchall()

            cur.execute(
                """SELECT A.uuid, A.title, A.update_date, B.display_name 
                    FROM sloth_posts AS A INNER JOIN sloth_post_types AS B ON B.uuid = A.post_type 
                    WHERE post_status = %s ORDER BY A.update_date DESC LIMIT 10;""",
                ('draft', )
            )
            raw_drafts = cur.fetchall()

            cur.execute(
                """SELECT uuid, sent_date, status 
                    FROM sloth_messages WHERE status != 'deleted' ORDER BY sent_date DESC LIMIT 10"""
            )
            raw_messages = cur.fetchall()

        except Exception as e:
            print(traceback.format_exc())
            abort(500)

        default_language = get_default_language(connection=connection)

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
                "sent_date": datetime.datetime.fromtimestamp(float(msg[1]) / 1000.0).strftime("%Y-%m-%d %H:%M"),
                "status": msg[2]
            })

        return render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
            template="dashboard.toe.html",
            data={
                "title": "Dashboard",
                "post_types": post_types_result,
                "permission_level": permission_level,
                "messages": messages,
                "recent_posts": recent_posts,
                "drafts": drafts,
                "upcoming_posts": upcoming_posts,
                "default_lang": default_language
            },
            hooks=Hooks()
        )


@dashboard.route("/api/dashboard-information")
@authorize_rest(0)
@db_connection_legacy
def dashboard_information(*args, connection=None, **kwargs):
    if connection is None:
        abort(500)

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    cur = connection.cursor()

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
        cur.close()
        connection.close()

        response = make_response(json.dumps({
            "post_types": post_types_result,
            "recentPosts": format_post_data(raw_recent_posts),
            "upcomingPosts": format_post_data(raw_upcoming_posts),
            "drafts": format_post_data(raw_drafts)
        }))
        code = 200
    except Exception as e:
        print(traceback.format_exc())
        connection.close()

        response = make_response(json.dumps({
            "error": True
        }))
        code = 500

    response.headers['Content-Type'] = 'application/json'
    return response, code


@dashboard.route("/api/dashboard-information/create-draft", methods=["POST"])
@authorize_rest(0)
@db_connection_legacy
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
                """INSERT INTO sloth_posts (uuid, title, slug, content, post_type, post_status, update_date, lang) 
                VALUES (%s, %s, %s, %s, %s, 'draft', %s, (SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language'))"""),
            [str(uuid.uuid4()), draft['title'], slug, draft['text'], draft['postType'], time() * 1000]
        )
        connection.commit()
        cur.execute(
            sql.SQL("SELECT uuid, title, publish_date, post_type FROM sloth_posts WHERE post_status = %s LIMIT 10"),
            ['draft']
        )
        raw_drafts = cur.fetchall()
        cur.close()
        connection.close()
        response = make_response(json.dumps({
            "drafts": format_post_data(raw_drafts)
        }))
        code = 200
    except Exception as e:
        print(traceback.format_exc())
        response = make_response(json.dumps({
            "error": True
        }))
        code = 500

    response.headers['Content-Type'] = 'application/json'
    return response, code


def format_post_data(post_arr):
    posts = []
    for post in post_arr:
        posts.append({
            "uuid": post[0],
            "title": post[1],
            "publishDate": post[2],
            "postType": post[3]
        })
    return posts
