from flask import request, flash, url_for, current_app, abort, redirect, render_template
from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web
from app.posts.post_types import PostTypes
import psycopg2
from psycopg2 import sql
import datetime
import uuid

from app.web.post import post


@post.route("/post/<post_type>")
@authorize_web(0)
@db_connection
def show_posts_list(*args, permission_level, connection, post_type, **kwargs):
    if connection is None:
        return redirect("/database-error")
    post_type_info = {
        "uuid": post_type
    }

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    cur = connection.cursor()

    raw_items = []
    # uuid, post_type, title, publish_date, update_date, post_status, categories, deleted
    try:
        cur.execute(
            sql.SQL("SELECT display_name FROM sloth_post_types WHERE uuid = %s"), [post_type]
        )

        post_type_info["name"] = cur.fetchall()[0][0]
        cur.execute(
            sql.SQL("""SELECT A.uuid, A.title, A.publish_date, A.update_date, A.post_status, B.display_name 
            FROM sloth_posts AS A INNER JOIN sloth_users AS B ON A.author = B.uuid 
            WHERE A.post_status = %s AND A.post_type = %s"""),
            ['published', post_type]
        )
        raw_items = cur.fetchall()
    except Exception as e:
        print("db error Q")
        abort(500)

    cur.close()
    connection.close()

    items = []
    for item in raw_items:
        items.append({
            "uuid": item[0],
            "title": item[1],
            "publish_date": datetime.datetime.fromtimestamp(float(item[2]) / 1000.0).strftime("%Y-%m-%d"),
            "update_date": datetime.datetime.fromtimestamp(float(item[3]) / 1000.0).strftime("%Y-%m-%d"),
            "status": item[4],
            "author": item[5]
        })

    return render_template("post-list.html",
                           post_types=post_types_result,
                           permission_level=permission_level,
                           post_list=items,
                           post_type=post_type_info,
                           )


@post.route("/post/<post_id>/edit")
@authorize_web(0)
@db_connection
def show_post_edit(*args, permission_level, connection, post_id, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    print("hello")

    cur = connection.cursor()
    media = []
    post_type_name = ""
    raw_post = {}
    try:
        cur.execute(
            sql.SQL("SELECT uuid, file_path, alt FROM sloth_media")
        )
        media = cur.fetchall()

        cur.execute(
            sql.SQL("""SELECT A.title, A.content, A.excerpt, A.css, A.use_theme_css, A.js, A.use_theme_js, A.thumbnail, 
            A.publish_date, A.update_date, A.post_status, A.tags, A.categories, B.display_name, A.post_type
                    FROM sloth_posts AS A INNER JOIN sloth_users AS B ON A.author = B.uuid WHERE A.uuid = %s"""),
            [post_id]
        )
        raw_post = cur.fetchone()
    except Exception as e:
        print("db error B")
        print(e)
        abort(500)

    cur.close()
    connection.close()

    token = request.cookies.get('sloth_session')

    data = {
        "uuid": post_id,
        "title": raw_post[0],
        "content": raw_post[1],
        "excerpt": raw_post[2],
        "css": raw_post[3],
        "use_theme_css": raw_post[4],
        "js": raw_post[5],
        "use_theme_js": raw_post[6],
        "thumbnail": raw_post[7],
        "publish_date": raw_post[8],
        "update_date": raw_post[9],
        "post_status": raw_post[10],
        "tags": raw_post[11],
        "categories": raw_post[12],
        "display_name": raw_post[13]
    }

    return render_template(
        "post-edit.html",
        post_types=post_types_result,
        permission_level=permission_level,
        token=token,
        post_type_name=post_type_name,
        data=data,
        media=media
    )


@post.route("/post/<post_type>/new")
@authorize_web(0)
@db_connection
def show_post_new(*args, permission_level, connection, post_type, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    cur = connection.cursor()
    media = []
    post_statuses = []
    try:

        cur.execute(
            sql.SQL("SELECT uuid, file_path, alt FROM sloth_media")
        )
        media = cur.fetchall()
        cur.execute(
            sql.SQL("SELECT display_name FROM sloth_post_types WHERE uuid = %s"),
            [post_type]
        )
        post_type_name = cur.fetchone()[0]
        cur.execute(
            sql.SQL("SELECT unnest(enum_range(NULL::sloth_post_status))")
        )
        temp_post_statuses = cur.fetchall()
    except Exception as e:
        print("db error A")
        abort(500)

    cur.close()
    connection.close()

    token = uuid.uuid4()

    post_statuses = [item for sublist in temp_post_statuses for item in sublist]

    return render_template("post-edit.html", post_types=post_types_result, permission_level=permission_level,
                           media=media, token=token, post_type_name=post_type_name, post_statuses=post_statuses,
                           data={"new": True, "use_theme_js": True, "use_theme_css": True, "status": "draft"})


@post.route("/post/<type_id>/taxonomy")
@authorize_web(0)
@db_connection
def show_post_taxonomy(*args, permission_level, connection, type_id, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    cur = connection.cursor()
    taxonomy = {}
    try:
        cur.execute(
            sql.SQL("SELECT unnest(enum_range(NULL::sloth_taxonomy_type))")
        )
        taxonomy_types = [item for sublist in cur.fetchall() for item in sublist]
        for taxonomy_type in taxonomy_types:
            cur.execute(
                sql.SQL("""SELECT uuid, display_name 
                FROM sloth_taxonomy WHERE post_type = %s AND taxonomy_type = %s"""),
                [type_id, taxonomy_type]
            )
            taxonomy[taxonomy_type] = cur.fetchall()
    except Exception as e:
        import pdb;
        pdb.set_trace()
        print("db error C")
        abort(500)

    cur.close()
    connection.close()

    return render_template(
        "taxonomy-list.html",
        post_types=post_types_result,
        permission_level=permission_level,
        taxonomy_list=taxonomy,
        post_uuid=type_id
    )


@post.route("/post/<type_id>/taxonomy/<taxonomy_id>", methods=["GET"])
@authorize_web(0)
@db_connection
def show_post_taxonomy_item(*args, permission_level, connection, type_id, taxonomy_id, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    cur = connection.cursor()
    temp_taxonomy = []
    try:
        cur.execute(
            sql.SQL("""SELECT slug, display_name 
            FROM sloth_taxonomy WHERE post_type = %s AND uuid = %s"""),
            [type_id, taxonomy_id]
        )
        temp_taxonomy = cur.fetchone()
    except Exception as e:
        import pdb;
        pdb.set_trace()
        print("db error C")
        abort(500)

    cur.close()
    connection.close()

    taxonomy = {
        "uuid": taxonomy_id,
        "post_uuid": type_id,
        "slug": temp_taxonomy[0],
        "display_name": temp_taxonomy[1]
    }

    return render_template(
        "taxonomy.html",
        post_types=post_types_result,
        permission_level=permission_level,
        taxonomy=taxonomy
    )


@post.route("/post/<type_id>/taxonomy/<taxonomy_id>", methods=["POST", "PUT"])
@authorize_web(0)
@db_connection
def save_post_taxonomy_item(*args, permission_level, connection, type_id, taxonomy_id, **kwargs):
    pass


@post.route("/post/<type_id>/taxonomy/<taxonomy_id>/delete", methods=["GET"])
@authorize_web(0)
@db_connection
def delete_post_taxonomy_item(*args, permission_level, connection, type_id, taxonomy_id, **kwargs):
    pass


@post.route("/post/<type_id>/taxonomy/new")
@authorize_web(0)
@db_connection
def create_taxonomy_item(*args, permission_level, connection, type_id, **kwargs):
    pass
