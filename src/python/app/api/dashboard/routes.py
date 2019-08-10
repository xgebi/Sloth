from flask import render_template, request, flash, redirect, url_for, current_app, abort

from pathlib import Path
import json
import os
import re
import psycopg2
from psycopg2 import sql, errors
import uuid
from time import time

from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize
from app.utilities.db_connection import db_connection

from app.api.dashboard import dashboard
from app.posts.post_types import PostTypes

@dashboard.route("/api/dashboard-information")
@authorize(0)
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
            sql.SQL("SELECT uuid, title, publish_date, post_type FROM sloth_posts WHERE post_status = %s LIMIT 10"), ['published']
        )
        raw_recent_posts = cur.fetchall()

        cur.execute(
            sql.SQL("SELECT uuid, title, publish_date, post_type FROM sloth_posts WHERE post_status = %s LIMIT 10"), ['scheduled']
        )
        raw_upcoming_posts = cur.fetchall()

        cur.execute(
            sql.SQL("SELECT uuid, title, publish_date, post_type FROM sloth_posts WHERE post_status = %s LIMIT 10"), ['draft']
        )
        raw_drafts = cur.fetchall()

    except Exception as e:
        print(e)
        abort(500)

    connection.close()
    return json.dumps({ 
        "postTypes": postTypesResult,
        "recentPosts": formatPostData(raw_recent_posts),
        "upcomingPosts": formatPostData(raw_upcoming_posts),
        "drafts": formatPostData(raw_drafts)
    })

@dashboard.route("/api/dashboard-information/create-draft", methods=["POST"])
@authorize(0)
@db_connection
def create_draft(*args, connection=None, **kwargs):
    if connection is None:
        abort(500)

    draft = json.loads(request.data)
    
    slug = re.sub('\s+', '-', draft['title'])
    slug = re.sub('[^0-9a-zA-Z\-]+', '', slug)

    cur = connection.cursor()
    print(draft)
    try:
        cur.execute(
            sql.SQL("INSERT INTO sloth_posts (uuid, title, slug, content, post_type, post_status, update_date) VALUES (%s, %s, %s, %s, %s, 'draft', %s)"),
            [str(uuid.uuid4()), draft['title'], slug, draft['text'], draft['postType'], time() * 1000]
        )
        connection.commit()
        cur.execute(
            sql.SQL("SELECT uuid, title, publish_date, post_type FROM sloth_posts WHERE post_status = %s LIMIT 10"), ['draft']
        )
        raw_drafts = cur.fetchall()
    except Exception as e:
        print(e)
        return json.dumps({ "error": "Database error"}), 500

    cur.close()
    connection.close()

    return json.dumps({ 
        "drafts": formatPostData(raw_drafts)
    })


def formatPostData(postArr):
    posts = [];
    for post in postArr:
        posts.append({
            "uuid": post[0],
            "title": post[1],
            "publishDate": post[2],
            "postType": post[3]
        })
    return posts