from flask import request, flash, url_for, current_app, abort
import json
import psycopg2
from psycopg2 import sql, errors
import uuid
from time import time
import os
import traceback
import re

from app.utilities.db_connection import db_connection
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize_rest
from app.utilities.db_connection import db_connection
from app.posts.posts_generator import PostsGenerator

from app.api.post import post

reserved_folder_names = ('tag', 'category')


@post.route("/api/post/media", methods=["GET"])
@authorize_rest(0)
@db_connection
def get_media_data(*args, connection, **kwargs):
    if connection is None:
        abort(500)

    cur = connection.cursor()
    raw_media = []
    try:

        cur.execute(
            sql.SQL("SELECT uuid, file_path, alt FROM sloth_media")
        )
        raw_media = cur.fetchall()
    except Exception as e:
        print("db error")
        abort(500)

    cur.close()
    connection.close()

    media = []
    for medium in raw_media:
        media.append({
            "uuid": medium[0],
            "filePath": medium[1],
            "alt": medium[2]
        })

    return json.dumps({"media": media})


@post.route("/api/post/upload-file", methods=['POST'])
@authorize_rest(0)
@db_connection
def upload_image(*args, file_name, connection=None, **kwargs):
    ext = file_name[file_name.rfind("."):]
    if not ext.lower() in (".png", ".jpg", ".jpeg", ".svg", ".bmp", ".tiff"):
        abort(500)
    with open(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", file_name), 'wb') as f:
        f.write(request.data)

    file = {}
    cur = connection.cursor()

    try:

        cur.execute(
            sql.SQL("INSERT INTO sloth_media VALUES (%s, %s, %s, %s) RETURNING uuid, file_path, alt"),
            [str(uuid.uuid4()), os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", file_name), "", ""]
        )
        file = cur.fetchone()
        cur.close()
    except Exception as e:
        print(traceback.format_exc())
        connection.close()
        abort(500)

    cur.close()
    connection.close()

    return json.dumps({"media": file}), 201


@post.route("/api/post", methods=['POST'])
@authorize_rest(0)
@db_connection
def save_post(*args, connection=None, **kwargs):
    if connection is None:
        abort(500)
    filled = json.loads(request.data)
    filled["thumbnail"] = filled["thumbnail"] if len(filled["thumbnail"]) > 0 else None
    cur = connection.cursor()
    try:
        # process tags
        cur.execute(
            sql.SQL("SELECT uuid, slug, display_name, post_type, taxonomy_type "
                    "FROM sloth_taxonomy WHERE post_type = %s AND taxonomy_type = 'tag';"),
            [filled["post_type_uuid"]]
        )
        existing_tags = cur.fetchall()
        trimmed_tags = [tag.strip() for tag in filled["tags"].split(",")]
        matched_tags = [tag[0] for tag in existing_tags if tag[2] in trimmed_tags]
        new_tags = [tag for tag in trimmed_tags if tag not in
                    [existing_tag[2] for existing_tag in existing_tags]]
        if len(new_tags) > 0:
            for new_tag in new_tags:
                slug = re.sub("\s+", "-", new_tag.strip())
                new_uuid = str(uuid.uuid4())
                cur.execute(
                    sql.SQL("""INSERT INTO sloth_taxonomy (uuid, slug, display_name, post_type, taxonomy_type) 
                                VALUES (%s, %s, %s, %s, 'tag');"""),
                    [new_uuid, slug, new_tag, filled["post_type_uuid"]]
                )
                matched_tags.append(new_uuid)
            connection.commit()
        # get user
        author = request.headers.get('authorization').split(":")[1]
        # save post
        if filled["new"]:
            unique_post = False
            while filled["new"] and not unique_post:
                cur.execute(
                    sql.SQL("SELECT count(uuid) FROM sloth_posts WHERE uuid = %s"),
                    [filled["uuid"]]
                )
                if cur.fetchone()[0] != 0:
                    filled["uuid"] = str(uuid.uuid4())
                else:
                    unique_post = True
                # TODO slug check
            publish_date = -1;
            if filled["post_status"] == 'published':
                publish_date = str(time() * 1000)
            elif filled["post_status"] == 'scheduled':
                publish_date = filled["scheduled_date"]  # TODO scheduling
            else:
                publish_date = None
            cur.execute(
                sql.SQL("""INSERT INTO sloth_posts (uuid, slug, post_type, author, 
                title, content, excerpt, css, js, thumbnail, publish_date, update_date, post_status, tags, 
                categories, lang) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'en')"""),
                [filled["uuid"], filled["slug"], filled["post_type_uuid"], author, filled["title"], filled["content"],
                 filled["excerpt"], filled["css"], filled["js"], filled["thumbnail"], publish_date, str(time() * 1000),
                 filled["post_status"], matched_tags, filled["categories"]]
            )
        else:
            cur.execute(
                sql.SQL("""UPDATE sloth_posts SET slug = %s, title = %s, content = %s, excerpt = %s, css = %s, js = %s,
                 thumbnail = %s, update_date = %s, post_status = %s, tags = %s, categories = %s WHERE uuid = %s;"""),
                [filled["slug"], filled["title"], filled["content"], filled["excerpt"], filled["css"], filled["js"],
                 filled["thumbnail"], str(time() * 1000), filled["post_status"], matched_tags,
                 filled["categories"], filled["uuid"]]
            )
        connection.commit()

        # get post
        if filled["post_status"] == 'published':
            cur.execute(
                sql.SQL("""SELECT uuid, original_lang_entry_uuid, lang, slug, post_type, author, title, content, 
                        excerpt, css, use_theme_css, js, use_theme_js, thumbnail, publish_date, update_date, 
                        post_status, tags, categories FROM sloth_posts WHERE uuid = %s;"""),
                [filled["uuid"]]
            )
            generatable_post = cur.fetchone()
            gen = PostsGenerator(connection=connection)
            gen.run(post={
                "uuid": generatable_post[0],
                "original_lang_entry_uuid": generatable_post[1],
                "lang": generatable_post[2],
                "slug": generatable_post[3],
                "post_type": generatable_post[4],
                "author": generatable_post[5],
                "title": generatable_post[6],
                "content": generatable_post[7],
                "excerpt": generatable_post[8],
                "css": generatable_post[9],
                "use_theme_css": generatable_post[10],
                "js": generatable_post[11],
                "use_theme_js": generatable_post[12],
                "thumbnail": generatable_post[13],
                "publish_date": generatable_post[14],
                "update_date": generatable_post[15],
                "post_status": generatable_post[16],
                "tags": generatable_post[17],
                "categories": generatable_post[18],
            })
    except Exception as e:
        return json.dumps({"error": str(e)}), 500

    cur.close()

    return json.dumps({"saved": True})


@post.route("/api/post/delete", methods=['POST', 'DELETE'])
@authorize_rest(0)
@db_connection
def delete_post(*args, permission_level, connection, **kwargs):
    if connection is None:
        abort(500)

    filled = json.loads(request.data)

    cur = connection.cursor()
    res = {}
    count = []
    try:
        cur.execute(
            sql.SQL("""SELECT A.post_type, A.slug, spt.slug 
            FROM sloth_posts as A INNER JOIN sloth_post_types spt on A.post_type = spt.uuid WHERE A.uuid = %s"""),
            [filled["post"]]
        )
        res = cur.fetchone()
        cur.execute(
            sql.SQL("DELETE FROM sloth_posts WHERE uuid = %s"),
            [filled["post"]]
        )
        connection.commit()
        cur.execute(
            sql.SQL("SELECT COUNT(uuid) FROM sloth_posts")
        )
        count = cur.fetchone()
    except Exception as e:
        abort(500)
    cur.close()
    gen = PostsGenerator(connection=connection)
    if count[0] == 0:
        gen.delete_post_type_post_files({"slug": res[2]})
    else:
        gen.delete_post_files({"slug": res[2]}, {"slug": res[1]})
        gen.run(post_type=res[2])

    return json.dumps(res[0])


@post.route("/api/post/taxonomy/<taxonomy_id>", methods=["DELETE"])
@authorize_rest(0)
@db_connection
def delete_taxonomy(*args, permission_level, connection, taxonomy_id, **kwargs):
    if connection is None:
        abort(500)

    cur = connection.cursor()

    try:
        cur.execute(
            sql.SQL("DELETE FROM sloth_taxonomy WHERE uuid = %s;"),
            [taxonomy_id]
        )
        connection.commit()
    except Exception as e:
        return json.dumps({"error": "db"})
    cur.close()
    connection.close()
    return json.dumps({"deleted": True})
