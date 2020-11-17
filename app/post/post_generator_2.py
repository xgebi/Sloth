from flask import current_app
from psycopg2 import sql, errors
from pathlib import Path
import os
from jinja2 import Template
import json

from app.utilities.db_connection import db_connection
from app.toes.markdown_parser import MarkdownParser


class PostGenerator:
    runnable = False
    theme_path = ""
    menus = {}

    @db_connection
    def __init__(self, *args, connection, **kwargs):
        if connection is None:
            return

        self.connection = connection
        self.config = current_app.config
        self.theme_path = self.get_theme_path()
        self.menus = self.get_menus()

    def get_theme_path(self, *args, **kwargs):
        cur = self.connection.cursor()
        active_theme = ""
        try:
            cur.execute(
                sql.SQL("""SELECT settings_name, settings_value, settings_value_type 
                        FROM sloth_settings WHERE settings_name = %s OR settings_type = %s"""),
                ['active_theme', 'sloth']
            )
            raw_item = cur.fetchone()
            active_theme = raw_item[1]
        except Exception as e:
            print(f"getting theme path error: {e}")

        cur.close()

        # Set path to the theme
        return Path(
            self.config["THEMES_PATH"],
            active_theme
        )

    def get_menus(self, *args, **kwargs):
        menus = {}
        cur = self.connection.cursor()
        try:
            cur.execute(
                sql.SQL("""SELECT name, uuid FROM sloth_menus""")
            )
            menus = {menu[0]: {"items": [], "uuid": menu[1], "name": [0]} for menu in cur.fetchall()}
            for menu in menus.keys():
                cur.execute(
                    sql.SQL("""SELECT title, url FROM sloth_menu_items WHERE menu = %s"""),
                    [menus[menu]["uuid"]]
                )
                menus[menu]["items"] = cur.fetchall()
        except Exception as e:
            print(f"PostGenerator.get_menus {e}")

        cur.close()
        return menus

    def get_protected_post(self, *args, uuid,**kwargs):
        post = {}
        try:
            cur = self.connection.cursor()
            # This is a rudimentary version
            cur.execute(
                sql.SQL("""SELECT title, excerpt, content, thumbnail 
                FROM sloth_posts WHERE uuid = %s;"""),
                [uuid]
            )
            raw_post = cur.fetchone()
            post["title"] = raw_post[0]
            md_parser = MarkdownParser()
            post["excerpt"] = md_parser.to_html_string(raw_post[1])
            post["content"] = md_parser.to_html_string(raw_post[2])
            if raw_post[3] is not None:
                cur.execute(
                    sql.SQL("""SELECT file_path, alt 
                                FROM sloth_media WHERE uuid = %s;"""),
                    [raw_post[3]]
                )
                raw_thumbnail = cur.fetchone()
                post["thumbnail"] = raw_thumbnail[0]
                post["thumbnail_alt"] = raw_thumbnail[1]
        except Exception as e:
            print(e)

        if os.path.isfile(os.path.join(self.theme_path, "secret.html")):
            with open(os.path.join(self.theme_path, "secret.html"), 'r') as f:
                protected_template = Template(f.read())
                return protected_template.render(post=post)

        else:
            return post
