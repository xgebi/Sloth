from flask import request, flash, url_for, current_app, abort, redirect, render_template
import psycopg2
from psycopg2 import sql

import app
import os
from pathlib import Path
import bcrypt
import json

from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web
from app.post.posts_generator import PostsGenerator

from app.post.post_types import PostTypes

from app.web.settings.themes import settings_themes


@settings_themes.route("/settings/themes")
@authorize_web(1)
@db_connection
def show_theme_settings(*args, permission_level, connection, **kwargs):
    if connection is None:
        return redirect("/database-error")
    settings = {}

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    config = current_app.config

    cur = connection.cursor()

    active_theme = ""
    try:
        cur.execute(
            "SELECT settings_value FROM sloth_settings WHERE settings_name = 'active_theme'"
        )
        raw_items = cur.fetchone()
        active_theme = raw_items[0]
    except Exception as e:
        print("db error")
        abort(500)

    cur.close()
    connection.close()

    list_of_dirs = os.listdir(config["THEMES_PATH"])
    themes = []

    for folder in list_of_dirs:
        theme_file = Path(config["THEMES_PATH"], folder, 'theme.json')
        if theme_file.is_file():
            with open(theme_file, 'r') as f:
                theme = json.loads(f.read())
                if theme["choosable"] and theme["name"].find(" ") == -1:
                    themes.append(theme)

    return render_template(
        "theme-list.html",
        post_types=post_types_result,
        permission_level=permission_level,
        themes=themes,
        active_theme=active_theme,
        regenarating=Path(os.path.join(os.getcwd(), 'generating.lock')).is_file()
    )


@settings_themes.route("/settings/themes/activate/<theme_name>")
@authorize_web(1)
@db_connection
def save_active_theme_settings(*args, theme_name, connection=None, **kwargs):
    # save theme theme to database
    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL("UPDATE sloth_settings SET settings_value = %s WHERE settings_name = 'active_theme';"),
            [theme_name]
        )
        connection.commit()
    except Exception as e:
        print("db error")
        abort(500)
    # regenerate all post
    posts_gen = PostsGenerator()
    posts_gen.run(posts=True)

    return redirect("/settings/themes")
