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
import shutil
import re
import collections
from jinja2 import Template
from app.post.post_types import PostTypes

from app.utilities.db_connection import db_connection


def get_menus(*args, connection, **kwargs):
    menus = {}
    cur = connection.cursor()
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
        print(traceback.format_exc())

    cur.close()
    return menus


class PostsGenerator:
    post = {}
    config = {}
    settings = {}
    is_runnable = True
    theme_path = ""
    connection = {}
    sloth_footer = ""
    menus = {}

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

        # Footer for post
        with open(Path(__file__).parent / "../templates/analytics.html", 'r') as f:
            footer_template = Template(f.read())
            cur = connection.cursor()
            raw_item = []
            try:
                cur.execute(
                    sql.SQL("""SELECT settings_value FROM sloth_settings 
                    WHERE settings_name = %s"""),
                    ['api_url']
                )
                raw_item = cur.fetchone()
            except Exception as e:
                print(traceback.format_exc())
            cur.close()
            if len(raw_item) == 1:
                self.sloth_footer = footer_template.render(api_url=raw_item[0])
            else:
                self.sloth_footer = ""

        # menus
        self.menus = get_menus(connection=connection)

    def run(self, post=False, posts=False, post_type=False):
        if not self.is_runnable and ((post and not posts) or (posts and not post)):
            return False
        t = {}

        if Path(os.path.join(os.getcwd(), 'generating.lock')).is_file():
            return self.add_to_queue(post=post, posts=posts, post_type=post_type)

        with open(os.path.join(os.getcwd(), 'generating.lock'), 'w') as f:
            f.write("generation locked")

        if posts:
            t = threading.Thread(target=self.generate_all)
        elif post:
            post_type = self.get_post_type(post["post_type"])
            t = threading.Thread(target=self.generate_post, kwargs=dict(post=post, post_type=post_type))
        elif post_type:
            t = threading.Thread(target=self.generate_post_type, kwargs=dict(post_type=post_type))
        else:
            os.remove(Path(os.path.join(os.getcwd(), 'generating.lock')))
            return False
        t.start()
        return True

    def add_to_queue(self, *args, post=False, posts=False, post_type=False, **kwargs):
        if post is not None:
            posts = [post]

    def get_post_type(self, uuid):
        cur = self.connection.cursor()
        raw_item = []
        try:
            cur.execute(
                sql.SQL("""SELECT uuid, slug, display_name, tags_enabled, categories_enabled, archive_enabled 
                                FROM sloth_post_types WHERE uuid = %s"""),
                [uuid]
            )
            raw_item = cur.fetchone()
        except Exception as e:
            print(traceback.format_exc())

        cur.close()

        return {
            "uuid": raw_item[0],
            "slug": raw_item[1],
            "display_name": raw_item[2],
            "tags_enabled": raw_item[3],
            "categories_enabled": raw_item[4],
            "archive_enabled": raw_item[5]
        }

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
                    A.publish_date, A.update_date, A.post_status, A.import_approved, A.thumbnail
                                FROM sloth_posts AS A INNER JOIN sloth_users AS B ON A.author = B.uuid
                                WHERE post_type = %s AND post_status = 'published' ORDER BY A.publish_date DESC;"""),
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
                taxonomies = self.get_taxonomy_for_post(post[0])
                thumbnail = None
                thumbnail_alt = None
                if post[13] is not None:
                    cur = self.connection.cursor()
                    try:
                        cur.execute(
                            sql.SQL("""SELECT file_path, alt FROM sloth_media WHERE uuid = %s;"""),
                            [post[13]]
                        )
                        raw_thumbnail = cur.fetchone()
                        thumbnail = raw_thumbnail[0]
                        thumbnail_alt = raw_thumbnail[1]
                    except Exception as e:
                        print(e)
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
                    "publish_date": post[9],
                    "publish_date_formatted": datetime.fromtimestamp(float(post[9]) / 1000).strftime("%Y-%m-%d %H:%M"),
                    "updated_date": post[10],
                    "update_date_formatted": datetime.fromtimestamp(float(post[10]) / 1000).strftime("%Y-%m-%d %H:%M"),
                    "post_status": post[11],
                    "tags": taxonomies["tags"],
                    "categories": taxonomies["categories"],
                    "post_type_slug": post_type["slug"],
                    "approved": post[12],
                    "thumbnail": thumbnail,
                    "thumbnail_alt": thumbnail_alt
                })

        return posts

    # Generate posts
    def generate_all(self):
        if Path(self.config["OUTPUT_PATH"], "assets").is_dir():
            shutil.rmtree(Path(self.config["OUTPUT_PATH"], "assets"))
        if Path(self.config["THEMES_PATH"], self.settings['active_theme']['settings_value'], "assets").is_dir():
            shutil.copytree(Path(self.config["THEMES_PATH"], self.settings['active_theme']['settings_value'], "assets"),
                            Path(self.config["OUTPUT_PATH"], "assets"))

        post_types = self.get_post_types()
        posts = self.get_posts_for_post_types(post_types)

        for post_type in post_types:
            tags = []
            categories = []
            for post in posts[post_type["uuid"]]:
                self.generate_post(post=post, post_type=post_type, multiple_posts=True)
                tags.append(post["tags"])
                categories.append(post["categories"])
            tags = self.remove_taxonomy_duplicates(taxonomy_list=tags)
            categories = self.remove_taxonomy_duplicates(taxonomy_list=categories)
            if post_type["tags_enabled"]:
                self.generate_tags(post_type_slug=post_type["slug"], tags=tags, posts=posts[post_type["uuid"]])

            if post_type["categories_enabled"]:
                self.generate_categories(post_type_slug=post_type["slug"], categories=categories,
                                         posts=posts[post_type["uuid"]])

            if post_type["archive_enabled"]:
                self.generate_archive(posts=posts[post_type["uuid"]], post_type=post_type)
                self.generate_rss(
                    posts=posts[post_type["uuid"]][:10],
                    path=Path(self.config["OUTPUT_PATH"], post_type["slug"])
                )

        self.generate_home()
        os.remove(Path(os.path.join(os.getcwd(), 'generating.lock')))

    def remove_taxonomy_duplicates(self, *args, taxonomy_list, **kwargs):
        taxonomies = {}
        taxonomies_list = []
        for taxo in taxonomy_list:
            for tax in taxo:
                taxonomies_list.append(tax)
        for taxonomy in taxonomies_list:
            if taxonomies.get(taxonomy["uuid"]) is None:
                taxonomies[taxonomy["uuid"]] = 1
            else:
                taxonomies[taxonomy["uuid"]] += 1
        to_delete = []
        for taxonomy in taxonomies.keys():
            while taxonomies[taxonomy] > 1:
                i = 0
                for t in taxonomies_list:
                    if t["uuid"] == taxonomy:
                        to_delete.append(i)
                        taxonomies[taxonomy] -= 1
                    i += 1
        to_delete.sort()
        for i in to_delete[::-1]:
            if (len(taxonomies_list) < i):
                print(i)
            taxonomies_list.pop(i)
        return taxonomies_list


    # Generate post
    def generate_post(self, *args, post, post_type, multiple_posts=False, **kwargs):
        post_path_dir = Path(self.config["OUTPUT_PATH"], post_type["slug"], post["slug"])
        self.theme_path = Path(self.config["THEMES_PATH"], self.settings['active_theme']['settings_value'])

        post_template_path = Path(self.theme_path, "post.html")
        if Path(self.theme_path, f"post-{post_type['slug']}.html").is_file():
            post_template_path = Path(self.theme_path, f"post-{post_type['slug']}.html")

        template = ""
        with open(post_template_path, 'r') as f:
            template = Template(f.read())

        if not os.path.exists(post_path_dir):
            os.makedirs(post_path_dir)

        with open(os.path.join(post_path_dir, 'index.html'), 'w') as f:
            f.write(template.render(post=post, sitename=self.settings["sitename"]["settings_value"],
                                    api_url=self.settings["api_url"]["settings_value"], sloth_footer=self.sloth_footer,
                                    menus=self.menus))

        if post["js"] and len(post["js"]) > 0:
            with open(os.path.join(post_path_dir, 'script.js'), 'w') as f:
                f.write(post["js"])

        if post["css"] and len(post["css"]) > 0:
            with open(os.path.join(post_path_dir, 'style.css'), 'w') as f:
                f.write(post["css"])

        if not multiple_posts:
            self.regenerate_for_post(post_type, post)
            if Path(os.path.join(os.getcwd(), 'generating.lock')).is_file():
                os.remove(Path(os.path.join(os.getcwd(), 'generating.lock')))

    def regenerate_for_post(self, post_type, post):
        # if tags_enabled, fetch list of posts for each tag
        # if categories_enabled, fetch list of posts for each tag
        # if archive_enabled, fetch all posts for post_type


        cur = self.connection.cursor()
        raw_items = []
        raw_tags = []
        raw_post_categories = []
        try:
            cur.execute(
                sql.SQL("""SELECT A.uuid, A.slug, B.display_name, B.uuid, A.title, A.content, A.excerpt, A.css, A.js,
                        sm.file_path, sm.alt, A.publish_date, A.update_date, A.post_status, A.import_approved, A.imported
                                    FROM sloth_posts AS A INNER JOIN sloth_users AS B ON A.author = B.uuid
                                    INNER JOIN sloth_media sm on sm.uuid = A.thumbnail
                                    WHERE post_type = %s AND post_status = 'published' ORDER BY A.publish_date DESC;"""),
                [post_type["uuid"]]
            )
            raw_items = cur.fetchall()
        except Exception as e:
            print(traceback.format_exc())

        posts = []

        for temp_post in raw_items:  # xgebi
            taxonomies = self.get_taxonomy_for_post(temp_post[0])
            posts.append({
                "uuid": temp_post[0],
                "slug": temp_post[1],
                "author_name": temp_post[2],
                "author_uuid": temp_post[3],
                "title": temp_post[4],
                "content": temp_post[5],
                "excerpt": temp_post[6],
                "css": temp_post[7],
                "js": temp_post[8],
                "thumbnail": temp_post[9],
                "thumbnail_alt": temp_post[10],
                "publish_date": temp_post[11],
                "update_date": temp_post[12],
                "publish_date_formatted": datetime.fromtimestamp(float(temp_post[11]) / 1000).strftime(
                    "%Y-%m-%d %H:%M"),
                "update_date_formatted": datetime.fromtimestamp(float(temp_post[12]) / 1000).strftime("%Y-%m-%d %H:%M"),
                "post_status": temp_post[13],
                "tags": taxonomies["tags"],
                "categories": taxonomies["categories"],
                "post_type_slug": post_type["slug"],
                "approved": temp_post[14],
                "imported": temp_post[15]
            })
        cur.close()

        if post_type["tags_enabled"]:
            self.generate_tags(post_type_slug=post_type["slug"], tags=post['tags'], posts=posts)

        if post_type["categories_enabled"]:
            self.generate_categories(post_type_slug=post_type["slug"], categories=post['categories'], posts=posts)

        if post_type["archive_enabled"]:
            self.generate_archive(posts=posts, post_type=post_type)
            self.generate_rss(
                posts=posts[:10],
                path=Path(self.config["OUTPUT_PATH"], post_type["slug"])
            )

        self.generate_home()

    # Generate tags
    def generate_tags(self, post_type_slug, tags, posts):
        if len(tags) == 0:
            return

        tags_posts_list = {}
        for tag in tags:
            tags_posts_list[tag["uuid"]] = []

            for post in posts:
                if tag["uuid"] in [temp_tag["uuid"] for temp_tag in post["tags"]]:
                    tags_posts_list[tag["uuid"]].append(post)

            tag_template_path = Path(self.theme_path, "tag.html")
            if Path(self.theme_path, f"tag-{post_type_slug}.html").is_file():
                tag_template_path = Path(self.theme_path, f"tag-{post_type_slug}.html")
            elif not tag_template_path.is_file():
                tag_template_path = Path(self.theme_path, "archive.html")

            template = ""
            with open(tag_template_path, 'r') as f:
                template = Template(f.read())

            post_path_dir = Path(self.config["OUTPUT_PATH"], post_type_slug, 'tag')

            if not os.path.exists(post_path_dir):
                os.makedirs(post_path_dir)

            if not os.path.exists(os.path.join(post_path_dir, tag["slug"])):
                os.makedirs(os.path.join(post_path_dir, tag["slug"]))

            for i in range(math.ceil(len(tags_posts_list[tag["uuid"]]) / 10)):
                if i > 0 and not os.path.exists(os.path.join(post_path_dir, tag["slug"], str(i))):
                    os.makedirs(os.path.join(post_path_dir, tag["slug"], str(i)))

                with open(os.path.join(post_path_dir, tag["slug"], str(i) if i != 0 else '', 'index.html'), 'w') as f:
                    lower = 10 * i
                    upper = (10 * i) + 10 if (10 * i) + 10 < len(tags_posts_list[tag["uuid"]]) else len(
                        tags_posts_list[tag["uuid"]])

                    f.write(template.render(
                        posts=tags_posts_list[tag["uuid"]][lower: upper],
                        tag=tag["uuid"],
                        sitename=self.settings["sitename"]["settings_value"],
                        page_name="Tag: " + tag["display_name"],
                        api_url=self.settings["api_url"]["settings_value"],
                        sloth_footer=self.sloth_footer,
                        menus=self.menus,
                        current_page_number=i,
                        not_last_page=True if math.ceil(len(tags_posts_list) / 10) != i else False
                    ))

    # Generate categories
    def generate_categories(self, post_type_slug, categories, posts):
        if len(categories) == 0:
            return

        categories_posts_list = {}
        for category in categories:
            categories_posts_list[category["uuid"]] = []

            for post in posts:
                if category in post["categories"]:
                    categories_posts_list[category["uuid"]].append(post)

            category_template_path = Path(self.theme_path, "category.html")
            if Path(self.theme_path, f"category-{post_type_slug}.html").is_file():
                category_template_path = Path(self.theme_path, f"category-{post_type_slug}.html")
            elif not category_template_path.is_file():
                category_template_path = Path(self.theme_path, "archive.html")

            template = ""
            with open(category_template_path, 'r') as f:
                template = Template(f.read())

            post_path_dir = Path(self.config["OUTPUT_PATH"], post_type_slug, 'category')

            if not os.path.exists(post_path_dir):
                os.makedirs(post_path_dir)

            if not os.path.exists(os.path.join(post_path_dir, category["slug"])):
                os.makedirs(os.path.join(post_path_dir, category["slug"]))

            for i in range(math.ceil(len(categories_posts_list[category["uuid"]]) / 10)):
                if i > 0 and not os.path.exists(os.path.join(post_path_dir, category["slug"], str(i))):
                    os.makedirs(os.path.join(post_path_dir, category["slug"], str(i)))

                with open(os.path.join(post_path_dir, category["slug"], str(i) if i != 0 else '', 'index.html'),
                          'w') as f:
                    lower = 10 * i
                    upper = (10 * i) + 10 if (10 * i) + 10 < len(categories_posts_list[category["uuid"]]) else len(
                        categories_posts_list[category["uuid"]])

                    f.write(template.render(
                        posts=categories_posts_list[category["uuid"]][lower: upper],
                        tag=category["uuid"],
                        sitename=self.settings["sitename"]["settings_value"],
                        page_name="Category: " + category["display_name"],
                        api_url=self.settings["api_url"]["settings_value"],
                        sloth_footer=self.sloth_footer,
                        menus=self.menus,
                        current_page_number=i,
                        not_last_page=True if math.ceil(len(categories_posts_list) / 10) != i else False
                    ))

    # Generate archive
    def generate_archive(self, posts, post_type):
        archive_template_path = Path(self.theme_path, "archive.html")
        if Path(self.theme_path, f"archive-{post_type['slug']}.html").is_file():
            archive_template_path = Path(self.theme_path, f"archive-{post_type['slug']}.html")

        template = ""
        with open(archive_template_path, 'r') as f:
            template = Template(f.read())

        post_path_dir = Path(self.config["OUTPUT_PATH"], post_type['slug'])

        if not os.path.exists(post_path_dir):
            os.makedirs(post_path_dir)

        for i in range(math.ceil(len(posts) / 10)):
            if i > 0 and not os.path.exists(os.path.join(post_path_dir, str(i))):
                os.makedirs(os.path.join(post_path_dir, str(i)))

            with open(os.path.join(post_path_dir, str(i) if i != 0 else '', 'index.html'), 'w') as f:
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
                    not_last_page=True if math.ceil(len(posts) / 10) != i else False
                ))

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
        for post in posts:
            if i >= 10:
                break
            i += 1
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
            content_text = doc.createCDATASection(post['content'])
            content.appendChild(content_text)
            post_item.appendChild(content)
            channel.appendChild(post_item)
        root_node.appendChild(channel)

        doc.writexml(
            open(str(os.path.join(path, "feed.xml")), 'w'),
            indent="  ",
            addindent="  ",
            newl='\n'
        )

    # Generate home page
    def generate_home(self):
        # get all post types
        post_types = PostTypes()
        post_type_list = post_types.get_post_type_list(self.connection)

        raw_posts = []
        try:
            cur = self.connection.cursor()
            cur.execute(
                sql.SQL("""SELECT A.uuid, A.slug, B.display_name, B.uuid, A.title, A.content, A.excerpt, A.css, A.js,
                    A.publish_date, A.update_date, A.post_status, C.slug, C.uuid
                                FROM sloth_posts AS A INNER JOIN sloth_users AS B ON A.author = B.uuid 
                                INNER JOIN sloth_post_types AS C ON A.post_type = C.uuid
                                WHERE C.archive_enabled = %s AND A.post_status = 'published' 
                                ORDER BY A.publish_date DESC"""),
                [True]
            )
            raw_posts = cur.fetchall()
            cur.close()
        except Exception as e:
            print(371)
            print(traceback.format_exc())

        rss_posts = []
        for post in raw_posts:
            cur = self.connection.cursor()
            raw_tags = []
            raw_post_categories = []
            taxonomies = self.get_taxonomy_for_post(post[0])
            rss_posts.append({
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
                "tags": taxonomies["tags"],
                "categories": taxonomies["categories"],
                "post_type_slug": post[12]
            })

        self.generate_rss(posts=rss_posts, path=Path(self.config["OUTPUT_PATH"]))

        # get 10 latest post for each post type
        posts = {}
        try:
            cur = self.connection.cursor()

            for post_type in post_type_list:
                cur.execute(
                    sql.SQL("""SELECT uuid, title, slug, excerpt, publish_date FROM sloth_posts 
                    WHERE post_type = %s AND post_status = 'published' ORDER BY publish_date DESC LIMIT 10"""),
                    [post_type['uuid']]
                )

                raw_items = cur.fetchall()
                temp_list = []
                for item in raw_items:
                    temp_list.append({
                        "uuid": item[0],
                        "title": item[1],
                        "slug": item[2],
                        "excerpt": item[3],
                        "publish_date": item[4],
                        "publish_date_formatted": datetime.fromtimestamp(float(item[4]) / 1000).strftime(
                            "%Y-%m-%d %H:%M"),
                        "post_type_slug": post_type['slug']
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
                sloth_footer=self.sloth_footer,
                menus=self.menus
            ))

    def generate_post_type(self, post_type):
        full_post_type = self.get_post_type(post_type)

        post_types = self.get_post_types()
        posts = self.get_posts_for_post_types(post_types)

        tags = set()
        categories = set()

        for post in posts:
            self.generate_post(post, post_type, multiple_posts=True)
            tags.update(post["tags"])
            categories.update(post["categories"])

        if full_post_type["tags_enabled"]:
            self.generate_tags(post_type_slug=post_type["slug"], tags=tags, posts=posts)

        if full_post_type["categories_enabled"]:
            self.generate_categories(post_type_slug=post_type["slug"], categories=categories, posts=posts)

        if full_post_type["archive_enabled"]:
            self.generate_archive(posts=posts[post_type["uuid"]], post_type=post_type)
            self.generate_rss(
                posts=posts[post_type["uuid"]][:10],
                path=Path(self.config["OUTPUT_PATH"], post_type["slug"])
            )

        self.generate_home()
        os.remove(Path(os.path.join(os.getcwd(), 'generating.lock')))

    # delete post files
    def delete_post_files(self, post_type, post):
        post_path_dir = Path(self.config["OUTPUT_PATH"], post_type["slug"], post["slug"])

        if os.path.exists(post_path_dir):
            shutil.rmtree(post_path_dir)

    # TODO to be tested
    def delete_post_type_post_files(self, post_type):
        posts_path_dir = Path(self.config["OUTPUT_PATH"], post_type["slug"])

        if os.path.exists(posts_path_dir):
            shutil.rmtree(posts_path_dir)

    def delete_taxonomy_files(self, post_type, taxonomy):
        posts_path_dir = Path(self.config["OUTPUT_PATH"], post_type["slug"], taxonomy)

        if os.path.exists(posts_path_dir):
            shutil.rmtree(Path(os.path.join(posts_path_dir, taxonomy)))

    def delete_archive_for_post_type(self, post_type):
        posts_path_dir = Path(self.config["OUTPUT_PATH"], post_type["slug"])

        if Path(os.path.join(posts_path_dir, 'index.html')).is_file():
            os.remove(Path(os.path.join(posts_path_dir, 'index.html')))

        for folder in [d for d in os.listdir(posts_path_dir) if re.search('\d+', d)]:
            shutil.rmtree(Path(os.path.join(posts_path_dir, folder)))

    def get_taxonomy_for_post(self, post_uuid):
        cur = self.connection.cursor()
        raw_tags = []
        raw_post_categories = []
        try:
            cur.execute(
                sql.SQL("""SELECT st.slug, st.display_name, st.uuid
                                            FROM sloth_post_taxonomies AS spt INNER JOIN sloth_taxonomy as st 
                                            ON spt.taxonomy = st.uuid
                                            WHERE spt.post = %s AND st.taxonomy_type = 'category';"""),

                [post_uuid]
            )
            raw_post_categories = cur.fetchall()
            cur.execute(
                sql.SQL("""SELECT st.slug, st.display_name, st.uuid
                                            FROM sloth_post_taxonomies AS spt INNER JOIN sloth_taxonomy as st 
                                            ON spt.taxonomy = st.uuid
                                            WHERE spt.post = %s AND st.taxonomy_type = 'tag';"""),
                [post_uuid]
            )
            raw_tags = cur.fetchall()
        except Exception as e:
            print(e)
        cur.close()
        return {
            "categories": self.process_taxonomy(taxonomy_list=raw_post_categories),
            "tags": self.process_taxonomy(taxonomy_list=raw_tags)
        }

    def process_taxonomy(self, *args, taxonomy_list, **kwargs):
        res_list = []
        for item in taxonomy_list:
            res_list.append({
                "uuid": item[2],
                "slug": item[0],
                "display_name": item[1]
            })
        return res_list
