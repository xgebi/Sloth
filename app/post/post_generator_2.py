from flask import current_app
from psycopg2 import sql, errors
from pathlib import Path
import os
from jinja2 import Template
import json
import threading

from app.utilities.db_connection import db_connection
from app.toes.markdown_parser import MarkdownParser


class PostGenerator:
    runnable = True
    theme_path = ""
    menus = {}

    @db_connection
    def __init__(self, *args, connection, **kwargs):
        if connection is None:
            self.is_runnable = False

        self.connection = connection
        self.config = current_app.config
        self.theme_path = self.get_theme_path()
        self.menus = self.get_menus()

        self.set_individual_settings(connection=connection, setting_name='active_theme')
        self.set_individual_settings(connection=connection, setting_name='main_language')

        # Set path to the theme
        self.theme_path = Path(
            self.config["THEMES_PATH"],
            self.settings['active_theme']['settings_value']
        )
        self.set_footer(connection=connection)

    def run(self, *args, post: str, post_type: str, everything: bool = True, **kwargs):
        """ Main function that runs everything

            Attributes
            ----------
            post: str
                Everything regarding a post will be regenerated
            post_type : str
                UUID of a post type, can be empty
            everything : bool
                Tells the function that everything will be regeneratable
        """
        if not self.runnable or (post and post_type):
            return False

        if Path(os.path.join(os.getcwd(), 'generating.lock')).is_file():
            # return self.add_to_queue(post=post)
            pass

        with open(os.path.join(os.getcwd(), 'generating.lock'), 'w') as f:
            f.write("generation locked")

        if post:
            pass
        elif post_type:
            pass
        elif everything:
            t = threading.Thread(target=self.generate_all)
        else:
            os.remove(Path(os.path.join(os.getcwd(), 'generating.lock')))
            return False
        t.start()
        return True

    def generate_all(self):
        pass

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

    def get_protected_post(self, *args, uuid, **kwargs):
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

    def set_footer(self, *args, connection, **kwargs):
        # Footer for post
        raw_api_url = []
        cur = connection.cursor()
        try:
            cur.execute(
                sql.SQL("""SELECT settings_value FROM sloth_settings 
                        WHERE settings_name = %s"""),
                ['api_url']
            )
            raw_api_url = cur.fetchone()
        except Exception as e:
            print(traceback.format_exc())
        cur.close()

        with open(Path(__file__).parent / "../templates/analytics.html", 'r') as f:
            footer_template = Template(f.read())
            cur = connection.cursor()
            raw_item = []

            if len(raw_api_url) == 1:
                self.sloth_footer = footer_template.render(api_url=raw_api_url[0])
            else:
                self.sloth_footer = ""

    def set_individual_settings(self, *args, connection, setting_name, **kwargs):
        cur = connection.cursor()
        try:
            cur.execute(
                sql.SQL("""SELECT settings_name, settings_value, settings_value_type 
                                FROM sloth_settings WHERE settings_name = %s OR settings_type = %s"""),
                [setting_name, 'sloth']
            )
            raw_items = cur.fetchall()
        except Exception as e:
            print(e)

        cur.close()

        for item in raw_items:
            self.settings[str(item[0])] = {
                "settings_name": item[0],
                "settings_value": item[1],
                "settings_value_type": item[2]
            }
