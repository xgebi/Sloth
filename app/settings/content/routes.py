from typing import List, Dict

import psycopg
from flask import abort, request, current_app, make_response
from werkzeug import utils as w_utils
import json
import os
import re
import uuid
from xml.dom import minidom
import dateutil.parser
from uuid import uuid4
import traceback
import zipfile
import shutil
from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web, authorize_rest
from app.toes.hooks import Hooks
from app.back_office.post.post_generator import PostGenerator
from app.back_office.post.post_types import PostTypes
from app.toes.toes import render_toe_from_path
from app.settings.content import content


@content.route("/settings/import")
@authorize_web(1)
@db_connection
def show_import_settings(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
    """
    Renders page that will show import options

    :param args:
    :param permission_level: int, indicates current permissions level that is needed to see this page
    :param connection:
    :param kwargs:
    """
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    # Import posts
    return render_toe_from_path(
        template="import-data.toe.html",
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        data={
            "title": "Import posts",
            "post_types": post_types_result,
            "permission_level": permission_level
        },
        hooks=Hooks()
    )


@content.route("/api/settings/import/wordpress", methods=["PUT", "POST"])
@authorize_rest(1)
@db_connection
def import_wordpress_content(*args, connection: psycopg.Connection, **kwargs):
    """
    API endpoint for importing Wordpress file

    :param args:
    :param connection:
    :param kwargs:
    """

    import_count = -1
    try:
        with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute("""SELECT settings_value FROM sloth_settings WHERE settings_name = 'wordpress_import_count';""")
            import_count = int(cur.fetchone()['settings_value']) + 1
            cur.execute("""UPDATE sloth_settings SET settings_value = %s WHERE settings_name = 
            'wordpress_import_count';""",
                        (import_count,))
            connection.commit()
    except Exception as e:
        print(e)
        connection.close()
        abort(500)

    uploads = {"filename": ""}

    if request.files.get("uploads"):
        uploads = request.files["uploads"]
        if uploads.mimetype == 'application/x-zip-compressed' and uploads.filename.endswith(".zip"):
            if not os.path.isdir(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "temp")):
                os.makedirs(os.path.join(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "temp")))

            with open(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "temp",
                                   w_utils.secure_filename(uploads.filename)),
                      'wb') as f:
                uploads.save(
                    os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "temp",
                                 w_utils.secure_filename(uploads.filename)))

            with zipfile.ZipFile(
                    os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "temp", uploads.filename),
                    'r') as zip_ref:
                zip_ref.extractall(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "temp", "uploaded"))

            files = os.listdir(
                os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "temp", "uploaded", "uploads"))
            for file in files:
                shutil.move(
                    os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "temp", "uploaded", "uploads",
                                 file),
                    os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content")
                )
            shutil.rmtree(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "temp", "uploaded"))

            os.remove(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "temp", uploads.filename))

    processed_state = -1
    if request.files.get("data"):
        xml_data = minidom.parse(request.files.get("data"))
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

        processed_state = process_attachments(attachments, connection, import_count)
        if processed_state == 1:
            rewrite_rules = process_posts(posts, connection, base_import_link, import_count)
            generator = PostGenerator()  # xgebi rewrite here when toes are in effect
            generator.run(everything=True)

            response = make_response(json.dumps({"rules": rewrite_rules, "media_uploaded": uploads.get("filename")}))
            code = 200

    if processed_state != 1:
        response = make_response(json.dumps({"error": "processing attachments"}))
        code = 500
    connection.close()

    response.headers['Content-Type'] = 'application/json'
    return response, code


def process_attachments(items: List, connection: psycopg.Connection, import_count: int) -> int:
    """
    Processes attachment from Wordpress

    :param items: List of items
    :param connection:
    :param import_count: number of times when import happened
    :return: -1 when unsuccessful and 1 when successful
    """
    for item in items:
        meta_infos = item.getElementsByTagName('wp:postmeta')
        alt = ""
        file_path = ""
        for info in meta_infos:
            if info.getElementsByTagName('wp:meta_key')[0].firstChild.wholeText == '_wp_attachment_image_alt':
                alt = info.getElementsByTagName('wp:meta_value')[0].firstChild.wholeText \
                    if info.getElementsByTagName('wp:meta_value')[0].firstChild is not None else ""
            if info.getElementsByTagName('wp:meta_key')[0].firstChild.wholeText == '_wp_attached_file':
                file_path = info.getElementsByTagName('wp:meta_value')[0].firstChild.wholeText \
                    if info.getElementsByTagName('wp:meta_value')[0].firstChild is not None else ""
        try:
            with connection.cursor() as cur:
                cur.execute("""INSERT INTO sloth_media (uuid, file_path, wp_id) VALUES (%s, %s, %s) RETURNING uuid""",
                            (str(uuid4()),
                             f"sloth-content/{file_path}",
                             f"{import_count}-{int(item.getElementsByTagName('wp:post_id')[0].firstChild.wholeText)}")
                            )
                uuid = cur.fetchone()[0]
                cur.execute("""INSERT INTO sloth_media_alts (uuid, media, lang, alt) 
                        VALUES (%s, %s, 
                        (SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language'), 
                        %s)""",
                            (str(uuid4()), uuid, "", alt)
                            )
                connection.commit()
        except Exception as e:
            print("100")
            print(traceback.format_exc())
            return -1

        cur.close()
        return 1


def process_posts(items: List, connection: psycopg.Connection, base_import_link: str, import_count: int):
    """
    Processes posts

    :param items: posts
    :param connection: connection to database
    :param base_import_link: Base link of the site from which it's imported
    :param import_count:  number of times when import happened
    :return:
    """
    try:
        with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute("SELECT slug, uuid FROM sloth_post_types")
            raw_post_types = cur.fetchall()
            cur.execute("SELECT settings_value FROM sloth_settings WHERE settings_name = 'site_url'")
            site_url = cur.fetchone()['settings_value']
            post_types = {}
            existing_categories = {}
            existing_tags = {}
            rewrite_rules = []
            for post_type in raw_post_types:
                post_types[post_type['uuid']] = post_type['uuid']

                taxonomies = fetch_taxonomies(cursor=connection, post_type=post_types[post_type['uuid']])
                existing_categories[post_type['uuid']] = taxonomies["categories"]
                existing_tags[post_type['uuid']] = taxonomies["tags"]

            for item in items:
                # title
                title = item.getElementsByTagName('title')[0].firstChild.wholeText
                # wp:post_type (attachment, nav_menu_item, illustration, page, post)
                post_type = item.getElementsByTagName('wp:post_type')[0].firstChild.wholeText
                if post_type not in post_types.keys():
                    cur.execute("""INSERT INTO sloth_post_types 
                                (uuid, slug, display_name, tags_enabled, categories_enabled, archive_enabled) 
                                VALUES (%s, %s, %s, True, True, True) RETURNING slug, uuid""",
                                (str(uuid4()), re.sub(r'\s+', '-', post_type), post_type))
                    returned = cur.fetchone()
                    cur.execute("""INSERT INTO sloth_post_formats (uuid, slug, display_name, post_type, deletable) 
                                VALUES (%s, %s, %s, %s, %s)""",
                                (str(uuid.uuid4()), "none", "None", returned[1], False))
                    connection.commit()
                    post_types[returned[0]] = returned[1]
                    existing_tags[returned[1]] = []
                    existing_categories[returned[1]] = []

                post_slug = re.sub(r'(-)+', '-', re.sub('[^0-9a-zA-Z\-]+', '', re.sub(r'(\s+|,)', '-', title))).lower()
                cur.execute(
                    """SELECT count(slug) FROM sloth_posts WHERE (slug LIKE %s OR slug LIKE %s) AND post_type = %s;""",
                    (f"{post_slug}-%", f"{post_slug}%", post_types[post_type]))
                similar = cur.fetchone()['count']
                if int(similar) > 0:
                    post_slug = f"{post_slug}-{str(int(similar) + 1)}"

                # link
                link = item.getElementsByTagName('link')[0].firstChild.wholeText
                # pubDate or wp:post_date
                pub_date = dateutil.parser.parse(
                    item.getElementsByTagName('pubDate')[0].firstChild.wholeText
                ).timestamp() * 1000 if item.getElementsByTagName('pubDate')[0].firstChild is not None else None
                # content:encoded (CDATA)
                content = item.getElementsByTagName('content:encoded')[0].firstChild.wholeText if \
                    item.getElementsByTagName('content:encoded')[0].firstChild is not None else ""
                excerpt = ""
                if len(content.split("<!--more-->")) == 2:
                    temp_content = content.split("<!--more-->")
                    content = "<p>" + re.sub("\n\n", "</p>\n\n<p>", temp_content[1]) + "</p>"
                    excerpt = temp_content[0]

                # images
                content = re.sub(f"{base_import_link}/wp-content/uploads/", f"{site_url}/sloth-content/", content)
                content = re.sub(f"-(\d+)x(\d+)\.", ".", content)

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
                        tags.append(thing.firstChild.wholeText)
                    if domain == 'category':
                        categories.append(thing.firstChild.wholeText)

                matched_tags = [tag for tag in existing_tags[post_types[post_type]] if tag["display_name"] in tags]
                new_tags = [tag for tag in tags if tag not in
                            [existing_tag["display_name"] for existing_tag in existing_tags[post_types[post_type]]]]
                matched_categories = [category for category in existing_categories[post_types[post_type]] if
                                      category["display_name"] in categories]
                new_categories = [category for category in categories if category not in
                                  [existing_category["display_name"] for existing_category in
                                   existing_categories[post_types[post_type]]]]
                if len(new_tags) > 0:
                    for new_tag in new_tags:
                        slug = re.sub("\s+", "-", new_tag.lower().strip())
                        new_uuid = str(uuid4())
                        try:
                            cur.execute("""INSERT INTO sloth_taxonomy 
                                                (uuid, slug, display_name, post_type, taxonomy_type) 
                                                    VALUES (%s, %s, %s, %s, 'tag');""",
                                        (new_uuid, slug, new_tag, post_types[post_type]))
                            matched_tags.append({"uuid": new_uuid})
                            existing_tags[post_types[post_type]].append({
                                "uuid": new_uuid,
                                "slug": slug,
                                "display_name": new_tag
                            })
                        except Exception as e:
                            print(e)
                    connection.commit()

                if len(new_categories) > 0:
                    for new_category in new_categories:
                        slug = re.sub("\s+", "-", new_category.strip())
                        new_uuid = str(uuid4())
                        try:
                            cur.execute("""INSERT INTO sloth_taxonomy (uuid, slug, display_name, post_type, taxonomy_type) 
                                                    VALUES (%s, %s, %s, %s, 'category');""",
                                        (new_uuid, slug, new_category, post_types[post_type]))
                            matched_categories.append({"uuid": new_uuid})
                            existing_categories[post_types[post_type]].append({
                                "uuid": new_uuid,
                                "slug": slug,
                                "display_name": new_category
                            })
                        except Exception as e:
                            print(e)
                    connection.commit()

                meta_infos = item.getElementsByTagName('wp:postmeta')
                thumbnail_id = ""
                for info in meta_infos:
                    if info.getElementsByTagName('wp:meta_key')[0].firstChild.wholeText == '_thumbnail_id':
                        thumbnail_id = info.getElementsByTagName('wp:meta_value')[0].firstChild.wholeText

                # uuid, title, slug, content, post_type, post_status, update_date, tags, categories
                post_uuid = str(uuid4())
                cur.execute("""INSERT INTO sloth_posts (uuid, slug, post_type, author, 
                                title, content, excerpt, css, js, thumbnail, publish_date, update_date, post_status, lang, imported) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, (SELECT uuid FROM sloth_media WHERE wp_id = %s LIMIT 1), %s, %s, %s, 'en', %s)""",
                            (post_uuid, post_slug, post_types[post_type],
                             request.headers.get('authorization').split(":")[1], title,
                             content, excerpt, "", "", f"{import_count}-{thumbnail_id}",
                             pub_date, pub_date, status, True))

                for tag in matched_tags:
                    cur.execute("""INSERT INTO sloth_post_taxonomies (uuid, post, taxonomy) VALUES (%s, %s, %s)""",
                                (str(uuid4()), post_uuid, tag["uuid"]))
                for category in matched_categories:
                    cur.execute("""INSERT INTO sloth_post_taxonomies (uuid, post, taxonomy) VALUES (%s, %s, %s)""",
                                (str(uuid4()), post_uuid, category["uuid"]))
                cur.execute("""SELECT sp.slug, spt.slug 
                            FROM sloth_posts as sp INNER JOIN sloth_post_types spt on sp.post_type = spt.uuid
                            WHERE sp.uuid = %s""",
                            (post_uuid,))
                slugs = cur.fetchone()
                if status == "published":
                    rewrite_rules.append(f"rewrite ^{link[len(base_import_link):]}$ /{slugs[1]}/{slugs[0]} permanent;")
            connection.commit()
        return rewrite_rules
    except Exception as e:
        print("117")
        print(traceback.format_exc())
        abort(500)


def fetch_taxonomies(*args, connection: psycopg.Connection, post_type: Dict, **kwargs) -> Dict:
    """
    Fetches existing taxonomies

    :param args:
    :param connection:
    :param post_type:
    :param kwargs:
    :return:
    """
    try:
        with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute("""SELECT uuid, slug, display_name FROM sloth_taxonomy
                             WHERE taxonomy_type = 'tag' AND post_type = %s""",
                        (post_type,))
            temp_tags = cur.fetchall()
            cur.execute("""SELECT uuid, slug, display_name FROM sloth_taxonomy 
                    WHERE taxonomy_type = 'category' AND post_type = %s""",
                        (post_type,))
            temp_categories = cur.fetchall()
    except Exception as e:
        print(e)
        return {
            "tags": [],
            "categories": []
        }
    return {
        "tags": temp_tags,
        "categories": temp_categories
    }


@content.route("/settings/export")
@authorize_web(1)
@db_connection
def show_export_settings(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
    """
    Renders page that will show export options

    :param args:
    :param permission_level:
    :param connection:
    :param kwargs:
    :return:
    """
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    # Import posts
    return render_toe_from_path(
        template="export-data.toe.html",
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        data={
            "title": "Import posts",
            "post_types": post_types_result,
            "permission_level": permission_level
        },
        hooks=Hooks()
    )
