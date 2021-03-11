from flask import request, abort, redirect, render_template, current_app
from psycopg2 import sql
import os
import json
from pathlib import Path

from app.utilities import get_default_language
from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web, authorize_rest

from app.post.post_types import PostTypes

from app.settings.dev import dev_settings


@dev_settings.route("/settings/dev")
@authorize_web(1)
@db_connection
def show_dev_settings(*args, permission_level, connection, **kwargs):
    if connection is None:
        return redirect("/database-error")

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    default_language = get_default_language(connection=connection)
    connection.close()

    if os.environ["FLASK_ENV"] != "development":
        return render_template("dev-settings-prod.html",
                               post_types=post_types_result,
                               permission_level=permission_level,
                               default_lang=default_language
                               )

    return render_template("dev-settings.html",
                           post_types=post_types_result,
                           permission_level=permission_level,
                           default_lang=default_language
                           )


@dev_settings.route("/api/settings/dev/posts", methods=["DELETE"])
@authorize_web(1)
@db_connection
def delete_posts(*args, permission_level, connection, **kwargs):
    if os.environ["FLASK_ENV"] != "development":
        abort(403)
    if connection is None:
        return redirect("/database-error")

    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL(
                """DELETE FROM sloth_posts;"""
            )
        )
        connection.commit()
    except Exception as e:
        print(e)
        abort(500)
    cur.close()
    connection.close()

    return json.dumps({"postsDeleted": True})


@dev_settings.route("/api/settings/dev/taxonomy", methods=["DELETE"])
@authorize_web(1)
@db_connection
def delete_taxonomy(*args, permission_level, connection, **kwargs):
    if os.environ["FLASK_ENV"] != "development":
        abort(403)
    if connection is None:
        return redirect("/database-error")

    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL(
                """DELETE FROM sloth_taxonomy;"""
            )
        )
        connection.commit()
    except Exception as e:
        print(e)
        abort(500)
    cur.close()
    connection.close()

    return json.dumps({"taxonomyDeleted": True})


@dev_settings.route("/api/settings/dev/health-check", methods=["GET"])
@authorize_web(0)
@db_connection
def check_posts_health(*args, permission_level, connection, **kwargs):
    if connection is None:
        abort(500)

    cur = connection.cursor()
    try:
        # from settings get default language
        cur.execute(
            sql.SQL("""SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language';""")
        )
        lang_id = cur.fetchone()[0]

        # from language_settings get short_name
        cur.execute(
            sql.SQL("""SELECT uuid, short_name FROM sloth_language_settings""")
        )
        raw_languages = cur.fetchall()
        languages = {lang[0]:lang[1] for lang in raw_languages}
        # from post_types get slugs
        cur.execute(
            sql.SQL("""SELECT uuid, slug FROM sloth_post_types""")
        )
        raw_post_types = cur.fetchall()
        post_types = {pt[0]: pt[1] for pt in raw_post_types}
        # from posts get slugs, post_type, language
        cur.execute(
            sql.SQL("""SELECT slug, post_type, lang FROM sloth_posts""")
        )
        posts = cur.fetchall()
        urls = [
            Path(os.path.join(
                current_app.config["OUTPUT_PATH"],
                languages[post[2]] if post[2] != lang_id else "",
                post_types[post[1]],
                post[0],
                "index.html"
            ))
            for post in posts
        ]
    except Exception as e:
        print(e)
        abort(500)

    cur.close()
    connection.close()

    if urls:
        urls_to_check = [str(url) for url in urls if not url.is_file()]
        return json.dumps({"urls": urls_to_check})
    else:
        abort(500)
