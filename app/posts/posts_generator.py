import psycopg2
from psycopg2 import sql, errors
from flask import current_app
from jinja2 import Template
from xml.dom import minidom

import threading
import time
from datetime import datetime
import os
import shutil
import math
from pathlib import Path
import traceback
from app.posts.post_types import PostTypes

from app.utilities.db_connection import db_connection


class PostsGenerator:
    post = {}
    config = {}
    settings = {}
    is_runnable = True
    theme_path = ""
    connection = {}
    sloth_footer = ""

    # Constructor
    @db_connection
    def __init__(self, *args, connection=None, **kwargs):
        # Connection to database is necessary to proceed
        if connection is None:
            self.is_runnable = False

        self.connection = connection
        self.config = current_app.config

        # Fetch settings
        cur = connection.cursor()
        try:
            cur.execute(
                sql.SQL("""SELECT settings_name, settings_value, settings_value_type 
                FROM sloth_settings WHERE settings_name = %s OR settings_type = %s"""),
                ['active_theme', 'sloth']
            )
            raw_items = cur.fetchall()
        except Exception as e:
            print(traceback.format_exc())

        cur.close()

        for item in raw_items:
            self.settings[str(item[0])] = {
                "settings_name": item[0],
                "settings_value": item[1],
                "settings_value_type": item[2]
            }

        # Set path to the theme
        self.theme_path = Path(
            self.config["THEMES_PATH"],
            self.settings['active_theme']['settings_value']
        )

        # Footer for posts
        with open(Path(__file__).parent / "../templates/analytics.html", 'r') as f:
            self.sloth_footer = f.read()

    def run(self, post=False, posts=False):
        # thread4hz = threading.Thread(target=countTo,kwargs=dict(x=3,delay=0.25))
        if not self.is_runnable and ((post and not posts) or (posts and not post)):
            return
        t = {}
        if posts:
            t = threading.Thread(target=self.generate_all)
        elif post:
            t = threading.Thread(target=self.generate_post, kwargs=dict(post=post))
        t.start()

    def get_post_type(self, uuid):
        post_type

    def get_post_types(self):
        cur = self.connection.cursor()
        raw_items = []
        try:
            cur.execute(
                sql.SQL("""SELECT uuid, slug, display_name, tags_enabled, categories_enabled, archive_enabled 
                        FROM sloth_post_types""")
            )
            raw_items = cur.fetchall()
        except Exception as e:
            print(traceback.format_exc())

        cur.close()

        post_types = []
        for item in raw_items:
            post_types.append({
                "uuid": item[0],
                "slug": item[1],
                "display_name": item[2],
                "tags_enabled": item[3],
                "categories_enabled": item[4],
                "archive_enabled": item[5]
            })

        return post_types

    def get_posts_for_post_types(self, post_types):
        cur = self.connection.cursor()
        raw_items = {}
        try:
            for post_type in post_types:
                cur.execute(
                    sql.SQL("""SELECT A.uuid, A.slug, B.display_name, B.uuid, A.title, A.content, A.excerpt, A.css, A.js,
                    A.thumbnail, A.publish_date, A.update_date, A.post_status, A.tags, A.categories
                                FROM sloth_posts AS A INNER JOIN sloth_users AS B ON A.author = B.uuid
                                WHERE post_type = %s AND post_status = 'published';"""),
                    [post_type["uuid"]]
                )
                raw_items[post_type["uuid"]] = cur.fetchall()
        except Exception as e:
            print(traceback.format_exc())

        cur.close()

        posts = {}
        for post_type in post_types:
            posts[post_type["uuid"]] = []

            for post in raw_items[post_type["uuid"]]:
                posts[post_type["uuid"]].append({
                    "uuid": post[0],
                    "slug": post[1],
                    "author_name": post[2],
                    "author_uuid": post[3],
                    "title": post[4],
                    "content": post[5],
                    "excerpt": post[6],
                    "css": post[7],
                    "js": post[8],
                    "thumbnail": post[9],
                    "publish_date": post[10],
                    "update_date": post[11],
                    "post_status": post[12],
                    "tags": post[13],
                    "categories": post[14],
                    "post_type_slug": post_type["slug"]
                })

        return posts

    # Generate posts
    def generate_all(self):
        post_types = self.get_post_types()
        posts = self.get_posts_for_post_types(post_types)

        for post in posts:
            self.generate_post(post, multiple_posts=True)

        if self.post["tags_enabled"]:
            self.generate_tags()

        if self.post["categories_enabled"]:
            self.generate_categories()

        if self.post["archive_enabled"]:
            self.generate_archive()

        self.generate_home()

    # Generate post
    def generate_post(self, post, multiple_posts=False):
        post_path_dir = Path(self.config["OUTPUT_PATH"], post["post_type_slug"], post["slug"])
        self.theme_path = Path(self.config["THEMES_PATH"], self.settings['active_theme']['settings_value'])

        post_template_path = Path(self.theme_path, "post.html")
        if Path(self.theme_path, "post-" + post["post_type_slug"] + ".html").is_file():
            post_template_path = Path(self.theme_path, "post-" + post["post_type_slug"] + ".html")

        template = ""
        with open(post_template_path, 'r') as f:
            template = Template(f.read())

        if not os.path.exists(post_path_dir):
            os.makedirs(post_path_dir)

        with open(os.path.join(post_path_dir, 'index.html'), 'w') as f:
            f.write(template.render(post=post, sitename=self.settings["sitename"]["settings_value"],
                                    api_url=self.settings["api_url"]["settings_value"]))

        if not multiple_posts:
            if self.post["tags_enabled"]:
                self.generate_tags()

            if self.post["categories_enabled"]:
                self.generate_categories()

            if self.post["archive_enabled"]:
                self.generate_archive()

            self.generate_home()

    # Generate tags
    def generate_tags(self, post_type_slug, tags):
        if len(tags) == 0:
            return

        tags_posts_list = {}
        for tag in tags:
            tags_posts_list[tag] = []
            cur = self.connection.cursor()
            raw_items = []
            try:
                cur.execute(
                    sql.SQL(
                        """SELECT uuid, title, publish_date FROM sloth_posts
                         WHERE post_type = %s AND %s = ANY (tags) AND post_status = %s"""
                    ),
                    [self.post["post_type"], tag, 'published']
                )
                raw_items = cur.fetchall()
            except Exception as e:
                print(traceback.format_exc())
            cur.close()

            for item in raw_items:
                tags_posts_list[tag].append({
                    "uuid": item[0],
                    "title": item[1],
                    "publish_date": item[2]
                })

            tag_template_path = Path(self.theme_path, "tag.html")
            if Path(self.theme_path, "tag-" + post_type_slug + ".html").is_file():
                tag_template_path = Path(self.theme_path, f"tag-{post_type_slug}.html")
            elif not tag_template_path.is_file():
                tag_template_path = Path(self.theme_path, "archive.html")

            template = ""
            with open(tag_template_path, 'r') as f:
                template = Template(f.read())

            for tag in tags:
                post_path_dir = Path(self.config["OUTPUT_PATH"], post_type_slug, 'tag')

                if not os.path.exists(post_path_dir):
                    os.makedirs(post_path_dir)

                if not os.path.exists(os.path.join(post_path_dir, tag)):
                    os.makedirs(os.path.join(post_path_dir, tag))

                for i in range(math.ceil(len(tags_posts_list[tag]) / 10)):
                    if i > 0 and not os.path.exists(os.path.join(post_path_dir, tag, str(i))):
                        os.makedirs(os.path.join(post_path_dir, tag, str(i)))

                    with open(os.path.join(post_path_dir, tag, str(i) if i != 0 else '', 'index.html'), 'w') as f:
                        lower = 10 * i
                        upper = (10 * i) + 10 if (10 * i) + 10 < len(tags_posts_list[tag]) else len(
                            tags_posts_list[tag])

                        f.write(template.render(
                            posts=tags_posts_list[tag][lower: upper],
                            tag=tag,
                            sitename=self.settings["sitename"]["settings_value"],
                            page_name="Tag: " + tag,
                            api_url=self.settings["api_url"]["settings_value"],
                            sloth_footer=self.sloth_footer
                        ))

    # Generate categories
    def generate_categories(self, post_type_slug, categories):
        if len(categories) == 0:
            return

        categories_posts_list = {}
        for category in categories:
            categories_posts_list[category] = []
            cur = self.connection.cursor()
            raw_items = []
            try:
                cur.execute(
                    sql.SQL(
                        """SELECT uuid, title, publish_date FROM sloth_posts
                         WHERE post_type = %s AND %s = ANY (categories) AND post_status = %s"""
                    ),
                    [self.post["post_type"], category, 'published']
                )
                raw_items = cur.fetchall()
            except Exception as e:
                print(traceback.format_exc())
            cur.close()

            for item in raw_items:
                categories_posts_list[category].append({
                    "uuid": item[0],
                    "title": item[1],
                    "publish_date": item[2]
                })

            tag_template_path = Path(self.theme_path, "tag.html")
            if Path(self.theme_path, "tag-" + self.post["post_type_slug"] + ".html").is_file():
                tag_template_path = Path(self.theme_path, "tag-" + self.post["post_type_slug"] + ".html")
            elif not tag_template_path.is_file():
                tag_template_path = Path(self.theme_path, "archive.html")

            template = ""
            with open(tag_template_path, 'r') as f:
                template = Template(f.read())

            for category in categories:
                post_path_dir = Path(self.config["OUTPUT_PATH"], self.post["post_type_slug"], 'tag')

                if not os.path.exists(post_path_dir):
                    os.makedirs(post_path_dir)

                if not os.path.exists(os.path.join(post_path_dir, category)):
                    os.makedirs(os.path.join(post_path_dir, category))

                for i in range(math.ceil(len(categories_posts_list[category]) / 10)):
                    if i > 0 and not os.path.exists(os.path.join(post_path_dir, category, str(i))):
                        os.makedirs(os.path.join(post_path_dir, category, str(i)))

                    with open(os.path.join(post_path_dir, category, str(i) if i != 0 else '', 'index.html'), 'w') as f:
                        lower = 10 * i
                        upper = (10 * i) + 10 if (10 * i) + 10 < len(categories_posts_list[category]) else len(
                            categories_posts_list[category])

                        f.write(template.render(
                            posts=categories_posts_list[category][lower: upper],
                            tag=category,
                            sitename=self.settings["sitename"]["settings_value"],
                            page_name="Tag: " + category,
                            api_url=self.settings["api_url"]["settings_value"],
                            sloth_footer=self.sloth_footer
                        ))

    # Generate archive

    # Generate rss
    def generate_rss(self, posts, path):
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

        i = 0
        for post in posts[::-1]:
            if i >= 10:
                break
            i += 1
            # <item>
            post_item = doc.createElement('item')
            post_item.setAttribute("guid", post['uuid'])
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
            # <pubDate>Wed, 28 Aug 2019 07:00:17 +0000</pubDate>
            pub_date = doc.createElement('pubDate')
            d = datetime.fromtimestamp(post['publish_date'] / 1000).astimezone()
            pub_date_text = doc.createTextNode(d.strftime('%a, %d %b %Y %H:%M:%S %z'))
            pub_date.appendChild(pub_date_text)
            post_item.appendChild(pub_date)

            # <dc:creator><![CDATA[Sarah Gebauer]]></dc:creator>
            # <category><![CDATA[Interesting links]]></category>
            for category in post['categories']:
                category_node = doc.createElement('category')
                category_text = doc.createCDATASection(category)
                category_node.appendChild(category_text)
                post_item.appendChild(category_node)
            # <content:encoded><![CDATA[
            description = doc.createElement('description')
            post_item.appendChild(description)

            content = doc.createElement('content:encoded')
            content_text = doc.createCDATASection(post['content'])
            content.appendChild(content_text)
            post_item.appendChild(content)
            channel.appendChild(post_item)
        root_node.appendChild(channel)

        doc.writexml(
            open(str(path) + "/feed.xml", 'w'),
            indent="  ",
            addindent="  ",
            newl='\n'
        )

    # Generate home page
    def generate_home(self):
        # get all post types
        post_types = PostTypes()
        post_type_list = post_types.get_post_type_list(self.connection)

        try:
            cur = self.connection.cursor()
            cur.execute(
                sql.SQL("SELECT uuid, slug FROM sloth_post_types")
            )
            raw_items = cur.fetchall()
            for item in raw_items:
                post_type_list.append({
                    "uuid": item[0],
                    "slug": item[1]
                })
            cur.close()
        except Exception as e:
            print(371)
            print(traceback.format_exc())

        # get 10 latest posts for each post type
        posts = {}
        try:
            cur = self.connection.cursor()
            for post_type in post_type_list:
                cur.execute(
                    sql.SQL("""SELECT uuid, title, slug, publish_date FROM sloth_posts 
                    WHERE post_type = %s AND post_status = %s ORDER BY publish_date DESC LIMIT 10"""),
                    [post_type['uuid'], 'published']
                )

                raw_items = cur.fetchall()
                temp_list = []
                for item in raw_items:
                    temp_list.append({
                        "uuid": item[0],
                        "title": item[1],
                        "slug": item[2],
                        "publish_date": item[3]
                    })
                posts[post_type['slug']] = temp_list
            cur.close()
        except Exception as e:
            print(390)
            print(traceback.format_exc())

        # get template
        home_template_path = Path(self.theme_path, "home.html")
        template = ""
        with open(home_template_path, 'r') as f:
            template = Template(f.read())

        # write file
        home_path_dir = Path(self.config["OUTPUT_PATH"], "index.html")

        with open(home_path_dir, 'w') as f:
            f.write(template.render(
                posts=posts, sitename=self.settings["sitename"]["settings_value"],
                page_name="Home", api_url=self.settings["api_url"]["settings_value"],
                sloth_footer=self.sloth_footer
            ))

    # delete post
