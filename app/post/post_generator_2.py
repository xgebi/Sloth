from flask import current_app
from psycopg2 import sql, errors
from pathlib import Path
import os
from jinja2 import Template
import json
import threading
import shutil
from typing import Dict, List
from datetime import datetime
import codecs
from xml.dom import minidom
import time
import math

from app.utilities.db_connection import db_connection
from app.toes.markdown_parser import MarkdownParser
from app.post.post_types import PostTypes


class PostGenerator:
    runnable = True
    theme_path = ""
    menus = {}

    @db_connection
    def __init__(self, *args, connection, **kwargs):
        self.settings = {}
        if connection is None:
            self.is_runnable = False

        self.connection = connection
        self.config = current_app.config
        self.menus = self.get_menus()

        self.set_individual_settings(connection=connection, setting_name='active_theme')
        self.set_individual_settings(connection=connection, setting_name='main_language')
        self.set_individual_settings(connection=connection, setting_name='number_rss_posts')

        # Set path to the theme
        self.theme_path = Path(
            self.config["THEMES_PATH"],
            self.settings['active_theme']['settings_value']
        )
        self.set_footer(connection=connection)

    def run(self, *args, post: str = "", post_type: str = "", everything: bool = True, **kwargs):
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
        if not self.runnable or (len(post) > 0 and len(post_type) > 0):
            return False

        if Path(os.path.join(os.getcwd(), 'generating.lock')).is_file():
            # return self.add_to_queue(post=post)
            return False

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
        if Path(self.config["OUTPUT_PATH"], "assets").is_dir():
            shutil.rmtree(Path(self.config["OUTPUT_PATH"], "assets"))
        if Path(self.config["THEMES_PATH"], self.settings['active_theme']['settings_value'], "assets").is_dir():
            shutil.copytree(Path(self.config["THEMES_PATH"], self.settings['active_theme']['settings_value'], "assets"),
                            Path(self.config["OUTPUT_PATH"], "assets"))

        # get languages
        languages = self.get_languages()
        # get post types
        post_types_object = PostTypes()
        post_types = post_types_object.get_post_type_list(self.connection)
        # generate posts for languages
        for language in languages:
            self.generate_posts_for_language(language=language, post_types=post_types)
        # remove lock
        os.remove(Path(os.path.join(os.getcwd(), 'generating.lock')))

    def generate_posts_for_language(self, *args, language: Dict[str, str], post_types: List[Dict[str, str]], **kwargs):
        if language["uuid"] == self.settings["main_language"]['settings_value']:
            # path for main language
            output_path = Path(self.config["OUTPUT_PATH"])
        else:
            # path for other languages
            output_path = Path(self.config["OUTPUT_PATH"], language["short_name"])

        for post_type in post_types:
            posts = self.get_posts_from_post_type_language(
                post_type_uuid=post_type['uuid'],
                post_type_slug=post_type['slug'],
                language_uuid=language['uuid']
            )
            self.delete_post_type_post_files(post_type=post_type, language=language)
            self.generate_post_type(posts=posts, output_path=output_path, post_type=post_type, language=language)
            # generate archive and RSS if enabled
            if post_type["archive_enabled"]:
                self.generate_archive(posts=posts, post_type=post_type, output_path=output_path, language=language)
                self.generate_rss(output_path=output_path, posts=posts)
        # generate home
        self.generate_home(output_path=output_path, post_types=post_types, language=language)

    def get_posts_from_post_type_language(
            self,
            *args,
            post_type_uuid: str,
            language_uuid: str,
            post_type_slug: str,
            **kwargs
    ):
        cur = self.connection.cursor()
        try:
            cur.execute(
                sql.SQL("""SELECT A.uuid, A.slug, B.display_name, B.uuid, A.title, A.content, A.excerpt, A.css, A.js,
                         A.publish_date, A.update_date, A.post_status, A.import_approved, A.thumbnail,
                         A.original_lang_entry_uuid
                                    FROM sloth_posts AS A INNER JOIN sloth_users AS B ON A.author = B.uuid
                                    WHERE post_type = %s AND lang = %s AND post_status = 'published' 
                                    ORDER BY A.publish_date DESC;"""),
                (post_type_uuid, language_uuid)
            )
            raw_items = cur.fetchall()
        except Exception as e:
            print(e)

        cur.close()

        posts = []

        for post in raw_items:
            thumbnail = None
            thumbnail_alt = None

            cur = self.connection.cursor()
            try:
                if post[13] is not None:
                    cur.execute(
                        sql.SQL("""SELECT file_path FROM sloth_media WHERE uuid = %s;"""),
                        (post[13],)
                    )
                    raw_thumbnail = cur.fetchone()
                    thumbnail = raw_thumbnail[0]

                if post[14]:
                    cur.execute(
                        sql.SQL(
                            """SELECT lang, slug FROM sloth_posts 
                            WHERE uuid = %s OR (original_lang_entry_uuid = %s AND uuid <> %s);"""
                        ),
                        (post[14], post[14], post[0])
                    )
                    temp_language_variants = cur.fetchall()
                else:
                    cur.execute(
                        sql.SQL(
                            """SELECT lang, slug FROM sloth_posts 
                            WHERE original_lang_entry_uuid = %s;"""
                        ),
                        (post[14],)
                    )
                    temp_language_variants = cur.fetchall()
            except Exception as e:
                print(e)

            language_variants = [{
                "lang": temp[0],
                "slug": temp[1]
            } for temp in temp_language_variants]
            posts.append({
                "uuid": post[0],
                "slug": post[1],
                "author_name": post[2],
                "author_uuid": post[3],
                "title": post[4],
                "content": post[5],
                "excerpt": post[6],
                "css": post[7],
                "js": post[8],
                "publish_date": post[9],
                "publish_date_formatted": datetime.fromtimestamp(float(post[9]) / 1000).strftime("%Y-%m-%d %H:%M"),
                "updated_date": post[10],
                "update_date_formatted": datetime.fromtimestamp(float(post[10]) / 1000).strftime("%Y-%m-%d %H:%M"),
                "post_status": post[11],
                "post_type_slug": post_type_slug,
                "approved": post[12],
                "thumbnail": thumbnail,
                "thumbnail_alt": thumbnail_alt,
                "language_variants": language_variants
            })

        return posts

    def generate_post_type(self, *args, posts, output_path, post_type, language, **kwargs):
        for post in posts:
            self.generate_post(post=post, output_path=output_path, post_type=post_type, language=language)

    def generate_post(self, *args, post, output_path, post_type, language, **kwargs):
        post_path_dir = Path(output_path, post_type["slug"], post["slug"])

        if os.path.isfile(os.path.join(self.theme_path, f"post-{post_type['slug']}-{language['short_name']}.html")):
            post_template_path = os.path.join(self.theme_path,
                                              f"post-{post_type['slug']}-{language['short_name']}.html")
        elif os.path.isfile(os.path.join(self.theme_path, f"post-{post_type['slug']}.html")):
            post_template_path = os.path.join(self.theme_path,
                                              f"post-{post_type['slug']}.html")
        else:
            post_template_path = Path(self.theme_path, "post.html")

        with open(post_template_path, 'r') as f:
            template = Template(f.read())

        if not os.path.exists(post_path_dir):
            os.makedirs(post_path_dir)

        with codecs.open(os.path.join(post_path_dir, 'index.html'), "w", "utf-8") as f:
            md_parser = MarkdownParser()
            post["excerpt"] = md_parser.to_html_string(post["excerpt"])
            post["content"] = md_parser.to_html_string(post["content"])
            rendered = template.render(
                post=post,
                sitename=self.settings["sitename"]["settings_value"],
                api_url=self.settings["api_url"]["settings_value"],
                sloth_footer=self.sloth_footer,
                menus=self.menus)
            f.write(rendered)

        if post["js"] and len(post["js"]) > 0:
            with open(os.path.join(post_path_dir, 'script.js'), 'w') as f:
                f.write(post["js"])

        if post["css"] and len(post["css"]) > 0:
            with open(os.path.join(post_path_dir, 'style.css'), 'w') as f:
                f.write(post["css"])

    def generate_archive(self, *args, posts, output_path, post_type, language, **kwargs):
        if len(posts) == 0:
            return

        archive_path_dir = Path(output_path, post_type["slug"])

        if os.path.isfile(os.path.join(self.theme_path, f"archive-{post_type['slug']}-{language['short_name']}.html")):
            archive_template_path = os.path.join(self.theme_path,
                                              f"archive-{post_type['slug']}-{language['short_name']}.html")
        elif os.path.isfile(os.path.join(self.theme_path, f"archive-{post_type['slug']}.html")):
            archive_template_path = os.path.join(self.theme_path,
                                              f"archive-{post_type['slug']}.html")
        else:
            archive_template_path = Path(self.theme_path, "archive.html")

        with open(archive_template_path, 'r') as f:
            template = Template(f.read())

        if not os.path.exists(archive_path_dir):
            os.makedirs(archive_path_dir)

        for i in range(math.ceil(len(posts) / 10)):
            if i > 0 and not os.path.exists(os.path.join(archive_path_dir, str(i))):
                os.makedirs(os.path.join(archive_path_dir, str(i)))

            path_to_index = os.path.join(archive_path_dir, str(i), 'index.html')
            if i == 0:
                path_to_index = os.path.join(archive_path_dir, 'index.html')

            with open(path_to_index, 'w') as f:
                lower = 10 * i
                upper = (10 * i) + 10 if (10 * i) + 10 < len(posts) else len(
                    posts)

                f.write(template.render(
                    posts=posts[lower: upper],
                    sitename=self.settings["sitename"]["settings_value"],
                    page_name=f"Archive for {post_type['display_name']}",
                    api_url=self.settings["api_url"]["settings_value"],
                    sloth_footer=self.sloth_footer,
                    menus=self.menus,
                    current_page_number=i,
                    not_last_page=True if math.floor(len(posts) / 10) != i else False
                ))

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
            print(e)
        cur.close()

        with open(Path(__file__).parent / "../templates/analytics.html", 'r') as f:
            footer_template = Template(f.read())
            cur = connection.cursor()
            raw_item = []

            if len(raw_api_url) == 1:
                self.sloth_footer = footer_template.render(api_url=raw_api_url[0])
            else:
                self.sloth_footer = ""

        with open(Path(__file__).parent / "../templates/secret-script.html", 'r') as f:
            # This will refactored
            secret_template = Template(f.read())

            if len(raw_api_url) == 1:
                self.sloth_secret_script = secret_template.render(api_url=raw_api_url[0])
            else:
                self.sloth_secret_script = ""

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

    def get_languages(self):
        cur = self.connection.cursor()
        try:
            cur.execute(
                sql.SQL("""SELECT uuid, long_name, short_name FROM sloth_language_settings""")
            )
            raw_items = cur.fetchall()
        except Exception as e:
            print(e)

        cur.close()

        languages = []
        for item in raw_items:
            languages.append({
                "uuid": item[0],
                "long_name": item[1],
                "short_name": item[2]
            })

        return languages

    # delete post files
    def delete_post_files(self, *args, post_type, post, language, **kwargs):
        post_type_slug = post_type
        post_slug = post
        if type(post) is not str:
            post_slug = post["slug"]
        if type(post_type) is not str:
            post_type_slug = post["slug"]
        if language["uuid"] == self.settings["main_language"]['settings_value']:
            # path for main language
            post_path_dir = Path(self.config["OUTPUT_PATH"], post_type_slug, post_slug)
        else:
            # path for other languages
            post_path_dir = Path(self.config["OUTPUT_PATH"], language["short_name"], post_type_slug, post_slug)

        if os.path.exists(post_path_dir):
            shutil.rmtree(post_path_dir)

    # delete post type files
    def delete_post_type_post_files(self, *args, post_type, language, **kwargs):
        if language["uuid"] == self.settings["main_language"]['settings_value']:
            # path for main language
            posts_path_dir = Path(self.config["OUTPUT_PATH"], post_type["slug"])
        else:
            # path for other languages
            posts_path_dir = Path(self.config["OUTPUT_PATH"], language["short_name"], post_type["slug"])

        if os.path.exists(posts_path_dir):
            shutil.rmtree(posts_path_dir)

    def generate_home(
            self,
            *args,
            output_path: Path,
            post_types: List[Dict[str, str]],
            language,
            **kwargs
    ):
        self.generate_rss(posts=self.prepare_rss_home_data(language=language), output_path=output_path)
        posts = {}
        try:
            cur = self.connection.cursor()

            for post_type in post_types:
                cur.execute(
                    sql.SQL(
                        """SELECT uuid, title, slug, excerpt, publish_date FROM sloth_posts 
                            WHERE post_type = %s AND post_status = 'published' AND lang = %s
                            ORDER BY publish_date DESC LIMIT %s"""
                    ),
                    (post_type['uuid'], language['uuid'], int(self.settings['number_rss_posts']['settings_value']))
                )
                raw_items = cur.fetchall()

                posts[post_type['slug']] = [{
                    "uuid": item[0],
                    "title": item[1],
                    "slug": item[2],
                    "excerpt": item[3],
                    "publish_date": item[4],
                    "publish_date_formatted": datetime.fromtimestamp(float(item[4]) / 1000).strftime(
                        "%Y-%m-%d %H:%M"),
                    "post_type_slug": post_type['slug']
                } for item in raw_items]
            cur.close()
        except Exception as e:
            print(390)
            print(e)

        # get template
        home_template_path = Path(self.theme_path, f"home-{language['short_name']}.html")
        if not home_template_path.is_file():
            home_template_path = Path(self.theme_path, f"home.html")

        with open(home_template_path, 'r') as f:
            template = Template(f.read())

        # write file
        home_path_dir = os.path.join(output_path, "index.html")

        with open(home_path_dir, 'w') as f:
            f.write(template.render(
                posts=posts, sitename=self.settings["sitename"]["settings_value"],
                page_name="Home", api_url=self.settings["api_url"]["settings_value"],
                sloth_footer=self.sloth_footer + self.sloth_secret_script,
                menus=self.menus
            ))

    def prepare_rss_home_data(self, *args, language, **kwargs):
        try:
            cur = self.connection.cursor()
            cur.execute(
                sql.SQL("""SELECT A.uuid, A.slug, B.display_name, B.uuid, A.title, A.content, A.excerpt, A.css, A.js,
                    A.publish_date, A.update_date, A.post_status, C.slug, C.uuid
                                FROM sloth_posts AS A INNER JOIN sloth_users AS B ON A.author = B.uuid 
                                INNER JOIN sloth_post_types AS C ON A.post_type = C.uuid
                                WHERE C.archive_enabled = %s AND A.post_status = 'published' AND A.lang = %s
                                ORDER BY A.publish_date DESC LIMIT %s"""),
                (True, language['uuid'], int(self.settings['number_rss_posts']['settings_value']))
            )
            raw_posts = cur.fetchall()
            cur.close()
        except Exception as e:
            print(371)
            print(e)

        return [{
            "uuid": post[0],
            "slug": post[1],
            "author_name": post[2],
            "author_uuid": post[3],
            "title": post[4],
            "content": post[5],
            "excerpt": post[6],
            "css": post[7],
            "js": post[8],
            "publish_date": post[9],
            "publish_date_formatted": datetime.fromtimestamp(float(post[9]) / 1000).strftime("%Y-%m-%d %H:%M"),
            "update_date": post[10],
            "update_date_formatted": datetime.fromtimestamp(float(post[10]) / 1000).strftime("%Y-%m-%d %H:%M"),
            "post_status": post[11],
            "post_type_slug": post[12]
        } for post in raw_posts]

    def generate_rss(self, *args, output_path: Path, posts, **kwargs):
        doc = minidom.Document()
        root_node = doc.createElement('rss')

        root_node.setAttribute('version', '2.0')
        root_node.setAttribute('xmlns:content', 'http://purl.org/rss/1.0/modules/content/')
        root_node.setAttribute('xmlns:wfw', 'http://wellformedweb.org/CommentAPI/')
        root_node.setAttribute('xmlns:dc', 'http://purl.org/dc/elements/1.1/')
        root_node.setAttribute('xmlns:atom', 'http://www.w3.org/2005/Atom')
        root_node.setAttribute('xmlns:sy', 'http://purl.org/rss/1.0/modules/syndication/')
        root_node.setAttribute('xmlns:slash', 'http://purl.org/rss/1.0/modules/slash/')
        doc.appendChild(root_node)

        channel = doc.createElement("channel")

        title = doc.createElement("title")
        title_text = doc.createTextNode(self.settings["sitename"]["settings_value"])
        title.appendChild(title_text)
        channel.appendChild(title)

        atom_link = doc.createElement("atom:link")
        atom_link.setAttribute('href', self.settings["site_url"]["settings_value"])
        atom_link.setAttribute('rel', 'self')
        atom_link.setAttribute('type', 'application/rss+xml')
        channel.appendChild(atom_link)

        link = doc.createElement('link')
        link_text = doc.createTextNode(self.settings["site_url"]["settings_value"])
        link.appendChild(link_text)
        channel.appendChild(link)

        description = doc.createElement('description')

        description_text = doc.createTextNode(self.settings["site_description"]["settings_value"])
        description.appendChild(description_text)
        channel.appendChild(description)
        # <lastBuildDate>Tue, 27 Aug 2019 07:50:51 +0000</lastBuildDate>
        last_build = doc.createElement('lastBuildDate')
        d = datetime.fromtimestamp(time.time()).astimezone()
        last_build_text = doc.createTextNode(d.strftime('%a, %d %b %Y %H:%M:%S %z'))
        last_build.appendChild(last_build_text)
        channel.appendChild(last_build)
        # <language>en-US</language>
        language = doc.createElement('language')
        language_text = doc.createTextNode('en-US')
        language.appendChild(language_text)
        channel.appendChild(language)
        # <sy:updatePeriod>hourly</sy:updatePeriod>
        update_period = doc.createElement('sy:updatePeriod')
        update_period_text = doc.createTextNode('hourly')
        update_period.appendChild(update_period_text)
        channel.appendChild(update_period)
        # <sy:updateFrequency>1</sy:updateFrequency>
        update_frequency = doc.createElement('sy:updateFrequency')
        update_frequency_text = doc.createTextNode('1')
        update_frequency.appendChild(update_frequency_text)
        channel.appendChild(update_frequency)
        # <generator>https://wordpress.org/?v=5.2.2</generator>
        generator = doc.createElement('generator')
        generator_text = doc.createTextNode('SlothCMS')
        generator.appendChild(generator_text)
        channel.appendChild(generator)

        for post in posts:
            # <item>
            post_item = doc.createElement('item')
            # <title>Irregular Batch of Interesting Links #10</title>
            post_title = doc.createElement('title')
            post_title_text = doc.createTextNode(post['title'])
            post_title.appendChild(post_title_text)
            post_item.appendChild(post_title)
            # <link>https://www.sarahgebauer.com/irregular-batch-of-interesting-links-10/</link>
            post_link = doc.createElement('link')

            post_link_text = doc.createTextNode(
                f"{self.settings['site_url']['settings_value']}/{post['post_type_slug']}/{post['slug']}")
            post_link.appendChild(post_link_text)
            post_item.appendChild(post_link)
            guid = doc.createElement("guid")
            guid.appendChild(doc.createTextNode(
                f"{self.settings['site_url']['settings_value']}/{post['post_type_slug']}/{post['slug']}"))
            post_item.appendChild(guid)
            # <pubDate>Wed, 28 Aug 2019 07:00:17 +0000</pubDate>
            pub_date = doc.createElement('pubDate')
            d = datetime.fromtimestamp(post['publish_date'] / 1000).astimezone()
            pub_date_text = doc.createTextNode(d.strftime('%a, %d %b %Y %H:%M:%S %z'))
            pub_date.appendChild(pub_date_text)
            post_item.appendChild(pub_date)

            # <dc:creator><![CDATA[Sarah Gebauer]]></dc:creator>
            # <category><![CDATA[Interesting links]]></category>
            # if isinstance(post['categories'], collections.Iterable):
            #    for category in post['categories']:
            #        category_node = doc.createElement('category')
            #        category_text = doc.createCDATASection(category["display_name"])
            #        category_node.appendChild(category_text)
            #        post_item.appendChild(category_node)
            # <content:encoded><![CDATA[
            description = doc.createElement('description')
            post_item.appendChild(description)

            content = doc.createElement('content:encoded')

            md_parser = MarkdownParser()
            if len(post["excerpt"]) == 0:
                post["content"] = md_parser.to_html_string(post["content"])
                content_text = doc.createCDATASection(post['content'])
            else:
                post["excerpt"] = md_parser.to_html_string(post["excerpt"])
                post["content"] = md_parser.to_html_string(post["content"])
                content_text = doc.createCDATASection(f"{post['excerpt']} {post['content']}")
            content.appendChild(content_text)
            post_item.appendChild(content)
            channel.appendChild(post_item)
        root_node.appendChild(channel)

        with codecs.open(os.path.join(output_path, "feed.xml"), "w", "utf-8") as f:
            f.write(doc.toprettyxml())
