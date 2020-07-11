from flask import request, flash, url_for, current_app, make_response, abort
import psycopg2
from psycopg2 import sql
import bcrypt
import json
import http.client
import os
import re
from xml.dom import minidom
import dateutil.parser
import uuid
import traceback
from datetime import datetime
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize_rest
from app.utilities.db_connection import db_connection
from app.posts.posts_generator import PostsGenerator

from app.api.content_management import content_management


@content_management.route("/api/content/information", methods=["GET"])
@authorize_rest(1)
@db_connection
def show_content(*args, connection=None, **kwargs):
    if connection is None:
        abort(500)

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    cur = connection.cursor()

    raw_items = []
    try:
        cur.execute(
            "SELECT settings_name, display_name, settings_value, settings_value_type FROM sloth_settings WHERE settings_type = 'sloth'"
        )
        raw_items = cur.fetchall()
    except Exception as e:
        print("db error a")
        abort(500)

    cur.close()
    connection.close()

    items = []
    for item in raw_items:
        items.append({
            "settingsName": item[0],
            "displayName": item[1],
            "settingsValue": item[2],
            "settingsValueType": item[3]
        })

    return json.dumps({"post_types": post_types_result, "settings": items})


@content_management.route("/api/content/import/wordpress", methods=["PUT", "POST"])
@authorize_rest(1)
@db_connection
def import_wordpress_content(*args, connection=None, **kwargs):
    if connection is None:
        return

    cur = connection.cursor()
    import_count = -1;
    try:
        cur.execute(
            sql.SQL("""SELECT settings_value FROM sloth_settings WHERE settings_name = 'wordpress_import_count';""")
        )
        import_count = int(cur.fetchone()[0]) + 1
        cur.execute(
            sql.SQL("""UPDATE sloth_settings SET settings_value = %s WHERE settings_name = 'wordpress_import_count';"""),
            [import_count]
        )
        connection.commit()
    except Exception as e:
        print(e)
        abort(500)

    xml_data = minidom.parseString(json.loads(request.data)["data"])
    base_import_link = xml_data.getElementsByTagName('wp:base_blog_url')[0].firstChild.wholeText
    items = xml_data.getElementsByTagName('item')
    posts = []
    attachments = []
    for item in items:
        post_type = item.getElementsByTagName('wp:post_type')[0].firstChild.wholeText
        if post_type == 'attachment':
            attachments.append(item)
        if post_type == 'post' or post_type == 'page':
            posts.append(item)

    process_attachments(attachments, connection, import_count)
    process_posts(posts, connection, base_import_link, import_count)
    generator = PostsGenerator()
    generator.run(posts=True)
    return json.dumps({"ok": True})


def process_attachments(items, connection, import_count):
    conn = {}
    now = datetime.now()
    for item in items:
        if conn == {}:
            conn = http.client.HTTPSConnection(item.getElementsByTagName('guid')[0].firstChild.wholeText[
                                               item.getElementsByTagName('guid')[0].firstChild.wholeText.find('//') + 2:
                                               item.getElementsByTagName('guid')[0].firstChild.wholeText.find('/', 8)])
        conn.request("GET", item.getElementsByTagName('guid')[0].firstChild.wholeText[
                            item.getElementsByTagName('guid')[0].firstChild.wholeText.find('/', 8):])
        res = conn.getresponse()

        data = res.read()

        if not os.path.exists(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content")):
            os.makedirs(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content"))

        if not os.path.exists(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", str(now.year))):
            os.makedirs(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", str(now.year)))

        if not os.path.exists(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", str(now.year), str(now.month))):
            os.makedirs(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", str(now.year), str(now.month)))

        filename = item.getElementsByTagName('guid')[0].firstChild.wholeText[
                   item.getElementsByTagName('guid')[0].firstChild.wholeText.rfind('/') + 1:]

        index = 1
        while os.path.exists(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", str(now.year), str(now.month), filename)):
            if filename[:filename.rfind('.')].endswith(f"-{index-1}"):
                filename = f"{filename[:filename.rfind('-')]}-{index}{filename[filename.rfind('.'):]}"
            else:
                filename = f"{filename[:filename.rfind('.')]}-{index}{filename[filename.rfind('.'):]}"
            index += 1

        with open(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", str(now.year), str(now.month), filename), 'wb') as f:
            f.write(data)
        meta_infos = item.getElementsByTagName('wp:postmeta')
        alt = ""
        for info in meta_infos:
            if info.getElementsByTagName('wp:meta_key')[0].firstChild.wholeText == '_wp_attachment_image_alt':
                alt = info.getElementsByTagName('wp:meta_value')[0].firstChild.wholeText
        try:
            cur = connection.cursor()
            cur.execute(
                sql.SQL("INSERT INTO sloth_media (uuid, file_path, alt, wp_id) VALUES (%s, %s, %s, %s)"),
                [str(uuid.uuid4()),
                 os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", str(now.year), str(now.month), filename),
                 alt, f"{import_count}-{int(item.getElementsByTagName('wp:post_id')[0].firstChild.wholeText)}"]
            )
            connection.commit()
        except Exception as e:
            print("100")
            print(traceback.format_exc())
            abort(500)

        cur.close()
    if conn:
        conn.close()


def process_posts(items, connection, base_import_link, import_count):
    try:
        cur = connection.cursor()
        cur.execute(
            sql.SQL("SELECT slug, uuid FROM sloth_post_types")
        )
        raw_post_types = cur.fetchall()
        cur.execute(
            sql.SQL("SELECT settings_value FROM sloth_settings WHERE settings_name = 'site_url'")
        )
        site_url = cur.fetchone()[0]
        now = datetime.now()
        post_types = {}
        existing_categories = {}
        existing_tags = {}
        for post_type in raw_post_types:
            post_types[post_type[0]] = post_type[1]

            taxonomies = fetch_taxonomies(cursor=cur, post_type=post_type)
            existing_categories[post_type[1]] = taxonomies["categories"]
            existing_tags[post_type[1]] = taxonomies["tags"]

        for item in items:
            # title
            title = item.getElementsByTagName('title')[0].firstChild.wholeText
            # wp:post_type (attachment, nav_menu_item, illustration, page, post)
            post_type = item.getElementsByTagName('wp:post_type')[0].firstChild.wholeText
            if not post_types[post_type]:
                cur.execute(
                    sql.SQL(
                        """INSERT INTO sloth_post_types 
                            (uuid, slug, display_name, tags_enabled, categories_enabled, archive_enabled) 
                            VALUES (%s, %s, %s, true, true, true) RETURNING slug, uuid"""
                    ),
                    [str(uuid.uuid4()), re.sub(r'\s+', '-', post_type), post_type]
                )
                returned = cur.fetchone()
                post_types[returned[0]] = returned[1]
            slug = re.sub('[^0-9a-zA-Z\-]+', '', re.sub(r'\s+', '-', title)).lower()
            cur.execute(
                sql.SQL("SELECT count(slug) FROM sloth_posts WHERE (slug LIKE %s OR slug LIKE %s) AND post_type = %s;"),
                [f"{slug}-%", f"{slug}%", post_types[post_type]]
            )
            similar = cur.fetchone()[0]
            if int(similar) > 0:
                slug = f"{slug}-{str(int(similar) + 1)}"

            # link
            link = item.getElementsByTagName('link')[0].firstChild.wholeText
            # pubDate or wp:post_date
            pub_date = dateutil.parser.parse(item.getElementsByTagName('pubDate')[0].firstChild.wholeText).timestamp()*1000
            # dc:creator (CDATA)
            creator = item.getElementsByTagName('dc:creator')[0].firstChild.wholeText
            # content:encoded (CDATA)
            content = item.getElementsByTagName('content:encoded')[0].firstChild.wholeText if \
                item.getElementsByTagName('content:encoded')[0].firstChild is not None else ""

            # images
            content = re.sub(f"{base_import_link}/wp-content/uploads/\d\d\d\d/\d\d/", f"{site_url}/{now.year}/{now.month}/", content)

            # wp:status (CDATA) (publish -> published, draft, scheduled?, private -> published)
            status = item.getElementsByTagName('wp:status')[0].firstChild.wholeText
            if status == "publish" or status == "private":
                status = "published"
            # category domain (post_tag, category) nicename
            categories = []
            tags = []
            for thing in item.getElementsByTagName('category'):
                domain = thing.getAttribute('domain')
                if domain == 'post_tag':
                    tags.append(thing.getAttribute('nicename'))
                if domain == 'category':
                    categories.append(thing.getAttribute('nicename'))

            matched_tags = [tag for tag in existing_tags[post_types[post_type]] if tag["display_name"] in tags]
            new_tags = [tag for tag in tags if tag not in
                        [existing_tag["display_name"] for existing_tag in existing_tags[post_types[post_type]]]]
            matched_categories = [category for category in existing_categories[post_types[post_type]] if category["display_name"] in categories]
            new_categories = [category for category in categories if category not in
                        [existing_category["display_name"] for existing_category in existing_categories[post_types[post_type]]]]
            if len(new_tags) > 0:
                for new_tag in new_tags:
                    slug = re.sub("\s+", "-", new_tag.strip())
                    new_uuid = str(uuid.uuid4())
                    try:
                        cur.execute(
                            sql.SQL("""INSERT INTO sloth_taxonomy (uuid, slug, display_name, post_type, taxonomy_type) 
                                                VALUES (%s, %s, %s, %s, 'tag');"""),
                            [new_uuid, slug, new_tag, post_types[post_type]]
                        )
                        matched_tags.append(new_uuid)
                    except Exception as e:
                        print(e)
                connection.commit()

            if len(new_categories) > 0:
                for new_category in new_categories:
                    slug = re.sub("\s+", "-", new_category.strip())
                    new_uuid = str(uuid.uuid4())
                    try:
                        cur.execute(
                            sql.SQL("""INSERT INTO sloth_taxonomy (uuid, slug, display_name, post_type, taxonomy_type) 
                                                VALUES (%s, %s, %s, %s, 'category');"""),
                            [new_uuid, slug, new_category, post_types[post_type]]
                        )
                        matched_categories.append(new_uuid)
                    except Exception as e:
                        print(e)
                connection.commit()

            meta_infos = item.getElementsByTagName('wp:postmeta')
            thumbnail_id = ""
            for info in meta_infos:
                if info.getElementsByTagName('wp:meta_key')[0].firstChild.wholeText == '_thumbnail_id':
                    thumbnail_id = info.getElementsByTagName('wp:meta_value')[0].firstChild.wholeText

            # uuid, title, slug, content, post_type, post_status, update_date, tags, categories
            cur.execute(
                sql.SQL("""INSERT INTO sloth_posts (uuid, slug, post_type, author, 
                            title, content, excerpt, css, js, thumbnail, publish_date, update_date, post_status, tags, 
                            categories, lang) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, (SELECT uuid FROM sloth_media WHERE wp_id = %s LIMIT 1), %s, %s, %s, %s, %s, 'en')"""),
                [str(uuid.uuid4()), slug, post_types[post_type], request.headers.get('authorization').split(":")[1], title, content, "", "", "", f"{import_count}-{thumbnail_id}",
                 pub_date, pub_date, status, [tag["uuid"] for tag in matched_tags], [category["uuid"] for category in matched_categories]]
            )
        connection.commit()
        cur.close()
    except Exception as e:
        print("117")
        print(traceback.format_exc())
        abort(500)


def fetch_taxonomies(*args, cursor, post_type, **kwargs):
    temp_tags = []
    temp_categories = []
    try:
        cursor.execute(
            sql.SQL("""SELECT uuid, slug, display_name FROM sloth_taxonomy
                         WHERE taxonomy_type = 'tag' AND post_type = %s"""),
            [post_type[1]]
        )
        temp_tags = cursor.fetchall()
        cursor.execute(
            sql.SQL(
                """SELECT uuid, slug, display_name FROM sloth_taxonomy 
                WHERE taxonomy_type = 'category' AND post_type = %s"""),
            [post_type[1]]
        )
        temp_categories = cursor.fetchall()
    except Exception as e:
        print(e)
    return {"tags": process_taxonomy(taxonomy_list=temp_tags), "categories": process_taxonomy(taxonomy_list=temp_categories)}


def process_taxonomy(*args, taxonomy_list, **kwargs):
    res_list = []
    for item in taxonomy_list:
        res_list.append({
            "uuid": item[0],
            "slug": item[1],
            "display_name": item[2]
        })
    return res_list

