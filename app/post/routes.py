from flask import request, flash, url_for, current_app, abort, redirect, render_template
import json
import psycopg2
from psycopg2 import sql, errors
import uuid
from time import time
import os
import traceback
import re
import datetime
from typing import List, Dict, Any

from app.post.post_types import PostTypes
from app.authorization.authorize import authorize_rest, authorize_web
from app.utilities.db_connection import db_connection
from app.utilities import get_languages, get_default_language, parse_raw_post, get_related_posts
from app.post.post_generator import PostGenerator

from app.post import post, get_translations

reserved_folder_names = ('tag', 'category')


# WEB
@post.route("/post/<post_type>")
@authorize_web(0)
@db_connection
def show_posts_list(*args, permission_level, connection, post_type, **kwargs):
    cur = connection.cursor()
    lang_id = ""
    try:
        cur.execute(
            sql.SQL("""SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language';""")
        )
        lang_id = cur.fetchone()[0]
    except Exception as e:
        print(e)
        abort(500)
    return return_post_list(permission_level=permission_level, connection=connection, post_type=post_type,
                            lang_id=lang_id)


@post.route("/post/<post_type>/<lang_id>")
@authorize_web(0)
@db_connection
def show_posts_list_language(*args, permission_level, connection, post_type, lang_id, **kwargs):
    return return_post_list(permission_level=permission_level, connection=connection, post_type=post_type,
                            lang_id=lang_id)


def return_post_list(*args, permission_level, connection, post_type, lang_id, **kwargs):
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
            WHERE A.post_type = %s AND A.lang = %s ORDER BY A.update_date DESC"""),
            [post_type, lang_id]
        )
        raw_items = cur.fetchall()
    except Exception as e:
        print("db error Q")
        abort(500)

    cur.close()
    current_lang, languages = get_languages(connection=connection, lang_id=lang_id)
    default_lang = get_default_language(connection=connection)
    connection.close()

    items = []
    for item in raw_items:
        items.append({
            "uuid": item[0],
            "title": item[1],
            "publish_date":
                datetime.datetime.fromtimestamp(float(item[2]) / 1000.0).
                    strftime("%Y-%m-%d") if item[2] is not None else "",
            "update_date":
                datetime.datetime.fromtimestamp(float(item[3]) / 1000.0).
                    strftime("%Y-%m-%d") if item[3] is not None else "",
            "status": item[4],
            "author": item[5]
        })

    return render_template("post-list.html",
                           post_types=post_types_result,
                           permission_level=permission_level,
                           post_list=items,
                           post_type=post_type_info,
                           languages=languages,
                           default_lang=default_lang,
                           current_lang=current_lang
                           )


@post.route("/post/<post_id>/edit")
@authorize_web(0)
@db_connection
def show_post_edit(*args, permission_level, connection, post_id, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    cur = connection.cursor()
    media = []
    post_type_name = ""
    raw_post = {}
    temp_thumbnail_info = []
    try:
        cur.execute(
            sql.SQL("SELECT uuid, file_path FROM sloth_media")
        )
        media = cur.fetchall()

        cur.execute(
            sql.SQL("""SELECT A.title, A.slug, A.content, A.excerpt, A.css, A.use_theme_css, A.js, A.use_theme_js,
             A.thumbnail, A.publish_date, A.update_date, A.post_status, B.display_name, A.post_type, A.imported, 
             A.import_approved, A.password, A.lang, A.original_lang_entry_uuid
                    FROM sloth_posts AS A INNER JOIN sloth_users AS B ON A.author = B.uuid WHERE A.uuid = %s"""),
            [post_id]
        )
        raw_post = cur.fetchone()
        cur.execute(
            sql.SQL("SELECT display_name FROM sloth_post_types WHERE uuid = %s"),
            [raw_post[13]]
        )
        post_type_name = cur.fetchone()[0]

        cur.execute(
            sql.SQL("""SELECT uuid, display_name, taxonomy_type FROM sloth_taxonomy
                                WHERE post_type = %s AND lang = %s"""),
            (raw_post[13], raw_post[17])
        )
        raw_all_taxonomies = cur.fetchall()
        cur.execute(
            sql.SQL("""SELECT taxonomy FROM sloth_post_taxonomies
                                        WHERE post = %s"""),
            (post_id, )
        )
        raw_post_taxonomies = cur.fetchall()
        cur.execute(
            sql.SQL("SELECT unnest(enum_range(NULL::sloth_post_status))")
        )
        temp_post_statuses = cur.fetchall()
        if raw_post[8] is not None:
            cur.execute(
                sql.SQL("""SELECT alt, 
                        concat((SELECT settings_value FROM sloth_settings WHERE settings_name = 'site_url'), '/',file_path)
                        FROM sloth_media WHERE uuid=%s"""),
                [raw_post[8]]
            )
            temp_thumbnail_info = cur.fetchone()
        current_lang, languages = get_languages(connection=connection, lang_id=raw_post[17])
        translatable = []
        if raw_post[18] is not None:
            # Get original
            # Get translations except current one
            cur.execute(
                sql.SQL("""SELECT uuid, lang FROM sloth_posts 
                WHERE (original_lang_entry_uuid=%s AND uuid != %s) OR (uuid = %s)"""),
                (post_id, post_id, raw_post[18])
            )
            temp_translations = cur.fetchall()
        else:
            cur.execute(
                sql.SQL("""SELECT uuid, lang FROM sloth_posts WHERE original_lang_entry_uuid=%s"""),
                (post_id,)
            )
            temp_translations = cur.fetchall()

        translated_languages = []
        for language in languages:
            addable = True
            for translation in temp_translations:
                if translation[1] == language['uuid']:
                    addable = False
                    translated_languages.append({
                        'uuid': translation[0],
                        'long_name': language['long_name']
                    })
            if addable:
                translatable.append(language)
    except Exception as e:
        print("db error B")
        print(e)
        abort(500)

    cur.close()
    default_lang = get_default_language(connection=connection)
    connection.close()

    token = request.cookies.get('sloth_session')

    publish_datetime = datetime.datetime.fromtimestamp(raw_post[9] / 1000) if raw_post[9] else None

    categories, tags = separate_taxonomies(taxonomies=raw_all_taxonomies, post_taxonomies=raw_post_taxonomies)

    data = {
        "uuid": post_id,
        "title": raw_post[0],
        "slug": raw_post[1],
        "content": raw_post[2],
        "excerpt": raw_post[3],
        "css": raw_post[4],
        "use_theme_css": raw_post[5],
        "js": raw_post[6],
        "use_theme_js": raw_post[7],
        "thumbnail_path": temp_thumbnail_info[1] if len(temp_thumbnail_info) >= 2 else None,
        "thumbnail_uuid": raw_post[8] if raw_post[8] is not None else "",
        "thumbnail_alt": temp_thumbnail_info[0] if len(temp_thumbnail_info) > 0 else None,
        "publish_date": publish_datetime.strftime("%Y-%m-%d") if publish_datetime else None,
        "publish_time": publish_datetime.strftime("%H:%M") if publish_datetime else None,
        "update_date": raw_post[10],
        "status": raw_post[11],
        "display_name": raw_post[12],
        "post_type": raw_post[13],
        "imported": raw_post[14],
        "approved": raw_post[15],
        "password": raw_post[16],
        "lang": raw_post[17],
        "categories": categories,
        "tags": tags
    }

    return render_template(
        "post-edit.html",
        post_types=post_types_result,
        permission_level=permission_level,
        token=token,
        post_type_name=post_type_name,
        data=data,
        media=media,
        post_statuses=[item for sublist in temp_post_statuses for item in sublist],
        default_lang=default_lang,
        languages=translatable,
        translations=translated_languages
    )


def separate_taxonomies(*args, taxonomies, post_taxonomies, **kwargs) -> (List[Dict], List[Dict]):
    categories = []
    tags = []

    flat_post_taxonomies = [pt[0] for pt in post_taxonomies]

    for raw_taxonomy in taxonomies:
        taxonomy = {
            "uuid": raw_taxonomy[0],
            "display_name": raw_taxonomy[1],
            "type": raw_taxonomy[2],
            "selected": True if raw_taxonomy[0] in flat_post_taxonomies else False
        }
        if taxonomy["type"] == 'category':
            categories.append(taxonomy)
        elif taxonomy["type"] == 'tag':
            tags.append(taxonomy)

    return categories, tags


@post.route("/post/<post_type>/new/<lang_id>")
@authorize_web(0)
@db_connection
def show_post_new(*args, permission_level, connection, post_type, lang_id, **kwargs):
    original_post = request.args.get('original');
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    cur = connection.cursor()
    media = []
    temp_post_statuses = []
    post_type_name = ""
    raw_all_categories = []
    try:

        cur.execute(
            sql.SQL("SELECT uuid, file_path FROM sloth_media")
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
        cur.execute(
            sql.SQL(
                "SELECT uuid, display_name FROM sloth_taxonomy WHERE taxonomy_type = 'category' AND post_type = %s;"),
            [post_type]
        )
        raw_all_categories = cur.fetchall()
        current_lang, languages = get_languages(connection=connection, lang_id=lang_id)
        default_lang = get_default_language(connection=connection)
        if original_post:
            translations, translatable_languages = get_translations(
                connection=connection,
                post_uuid="",
                original_entry_uuid=original_post,
                languages=languages
            )
        else:
            translatable_languages = languages
            translations = []
    except Exception as e:
        print("db error A")
        abort(500)

    cur.close()
    connection.close()

    post_statuses = [item for sublist in temp_post_statuses for item in sublist]

    all_categories = []
    for category in raw_all_categories:
        selected = False
        all_categories.append({
            "uuid": category[0],
            "display_name": category[1],
            "selected": selected
        })

    data = {
        "new": True,
        "use_theme_js": True,
        "use_theme_css": True,
        "status": "draft",
        "uuid": uuid.uuid4(),
        "post_type": post_type,
        "lang": lang_id,
        "original_post": original_post
    }

    return render_template("post-edit.html", post_types=post_types_result, permission_level=permission_level,
                           media=media, post_type_name=post_type_name, post_statuses=post_statuses,
                           data=data, all_categories=all_categories, default_lang=default_lang,
                           current_lang_id=lang_id, languages=translatable_languages, translations=translations)


@post.route("/post/<type_id>/taxonomy")
@authorize_web(0)
@db_connection
def show_post_taxonomy_main_lang(*args, permission_level, connection, type_id, **kwargs):
    return show_taxonomy(
        permission_level=permission_level,
        connection=connection,
        type_id=type_id,
        lang_id=get_default_language(connection=connection)["uuid"]
    )


@post.route("/post/<type_id>/taxonomy/<lang_id>")
@authorize_web(0)
@db_connection
def show_post_taxonomy(*args, permission_level, connection, type_id, lang_id, **kwargs):
    return show_taxonomy(
        permission_level=permission_level,
        connection=connection,
        type_id=type_id,
        lang_id=lang_id
    )


def show_taxonomy(*args, permission_level, connection, type_id, lang_id, **kwargs):
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
                FROM sloth_taxonomy WHERE post_type = %s AND taxonomy_type = %s AND lang = %s"""),
                (type_id, taxonomy_type, lang_id)
            )
            taxonomy[taxonomy_type] = cur.fetchall()
    except Exception as e:
        import pdb;
        pdb.set_trace()
        print("db error C")
        abort(500)

    cur.close()
    # current_lang, languages = get_languages(connection=connection, lang_id=lang_id)
    default_language = get_default_language(connection=connection)
    current_lang, languages = get_languages(connection=connection, lang_id=lang_id)

    connection.close()

    return render_template(
        "taxonomy-list.html",
        post_types=post_types_result,
        permission_level=permission_level,
        taxonomy_types=taxonomy_types,
        taxonomy_list=taxonomy,
        post_type_uuid=type_id,
        default_lang=default_language,
        languages=languages
    )


@post.route("/post/<type_id>/taxonomy/<taxonomy_type>/<taxonomy_id>", methods=["GET"])
@authorize_web(0)
@db_connection
def show_post_taxonomy_item(*args, permission_level, connection, type_id, taxonomy_id, taxonomy_type, **kwargs):
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
    default_language = get_default_language(connection=connection)
    current_lang, languages = get_languages(connection=connection)
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
        taxonomy=taxonomy,
        taxonomy_type=taxonomy_type,
        default_lang=default_language,
        current_lang_uuid=current_lang["uuid"]
    )


@post.route("/post/<type_id>/taxonomy/<taxonomy_type>/<taxonomy_id>", methods=["POST", "PUT"])
@authorize_web(0)
@db_connection
def save_post_taxonomy_item(*args, permission_level, connection, type_id, taxonomy_id, taxonomy_type, **kwargs):
    cur = connection.cursor()
    filled = request.form

    if filled["slug"] or filled["display_name"]:
        redirect(f"/post/{type_id}/taxonomy/{taxonomy_id}?error=missing_data")
    try:
        cur.execute(
            sql.SQL("SELECT display_name FROM sloth_taxonomy WHERE uuid = %s;"),
            [taxonomy_id]
        )
        res = cur.fetchall()
        if len(res) == 0:
            cur.execute(
                sql.SQL(
                    """INSERT INTO sloth_taxonomy (uuid, slug, display_name, post_type, taxonomy_type, lang) 
                    VALUES (%s, %s, %s, %s, %s, %s);"""
                ),
                (taxonomy_id, filled["slug"], filled["display_name"], type_id, taxonomy_type, filled["language"])
            )
        else:
            cur.execute(sql.SQL("""UPDATE sloth_taxonomy SET slug = %s, display_name = %s WHERE uuid = %s;"""),
                        [filled["slug"], filled["display_name"], taxonomy_id])
        connection.commit()
    except Exception as e:
        return redirect(f"/post/{type_id}/taxonomy/{taxonomy_type}/{taxonomy_id}?error=db")
    cur.close()
    connection.close()
    return redirect(f"/post/{type_id}/taxonomy/{taxonomy_type}/{taxonomy_id}")


@post.route("/post/<type_id>/taxonomy/<taxonomy_type>/new")
@authorize_web(0)
@db_connection
def create_taxonomy_item(*args, permission_level, connection, type_id, taxonomy_type, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    default_language = get_default_language(connection=connection)
    current_lang, languages = get_languages(connection=connection)
    connection.close()

    taxonomy = {
        "uuid": uuid.uuid4(),
        "post_uuid": type_id
    }

    return render_template(
        "taxonomy.html",
        post_types=post_types_result,
        permission_level=permission_level,
        taxonomy=taxonomy,
        taxonomy_type=taxonomy_type,
        new=True,
        default_lang=default_language,
        current_lang_uuid=current_lang['uuid']
    )


# API
@post.route("/api/post/media/<lang_id>", methods=["GET"])
@authorize_rest(0)
@db_connection
def get_media_data(*args, connection, lang_id: str, **kwargs):
    if connection is None:
        abort(500)

    cur = connection.cursor()
    site_url = ""
    media = []
    try:
        cur.execute(
            sql.SQL("SELECT settings_value FROM sloth_settings WHERE settings_name = 'site_url'")
        )
        site_url = cur.fetchone()
        site_url = site_url[0] if len(site_url) > 0 else ""
        cur.execute(
            sql.SQL("SELECT uuid, file_path FROM sloth_media")
        )
        raw_media = cur.fetchall()
        media = {medium[0]: {
            "uuid": medium[0],
            "filePath": f"{site_url}/{medium[1]}"
        } for medium in raw_media}
        languages = get_languages(connection=connection)
        cur.execute(
            sql.SQL(
                """SELECT media, alt FROM sloth_media_alts
                           WHERE lang = %s;"""
            ),
            (lang_id,)
        )
        alts = cur.fetchall()
        for alt in alts:
            if media[alt[0]] is not None:
                media[alt[0]]["alt"] = alt[1]
    except Exception as e:
        print("db error")
        abort(500)

    cur.close()
    connection.close()

    return json.dumps({"media": list(media.values())})


@post.route("/api/post/upload-file", methods=['POST'])
@authorize_rest(0)
@db_connection
def upload_image(*args, file_name, connection=None, **kwargs):
    ext = file_name[file_name.rfind("."):]
    if not ext.lower() in (".png", ".jpg", ".jpeg", ".svg", ".bmp", ".tiff"):
        abort(500)
    with open(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", file_name), 'wb') as f:
        f.write(request.data)

    file = {}
    cur = connection.cursor()

    try:

        cur.execute(
            sql.SQL("INSERT INTO sloth_media VALUES (%s, %s, %s, %s) RETURNING uuid, file_path, alt"),
            [str(uuid.uuid4()), os.path.join("sloth-content", file_name), "", ""]
        )
        file = cur.fetchone()
        cur.close()
    except Exception as e:
        print(traceback.format_exc())
        connection.close()
        abort(500)

    cur.close()
    connection.close()

    return json.dumps({"media": file}), 201


@post.route("/api/post", methods=['POST'])
@authorize_rest(0)
@db_connection
def save_post(*args, connection=None, **kwargs):
    if connection is None:
        abort(500)
    result = {}
    filled = json.loads(request.data)
    filled["thumbnail"] = filled["thumbnail"] if len(filled["thumbnail"]) > 0 else None
    cur = connection.cursor()
    try:
        # process tags
        cur.execute(
            sql.SQL("SELECT uuid, slug, display_name, post_type, taxonomy_type "
                    "FROM sloth_taxonomy WHERE post_type = %s AND taxonomy_type = 'tag';"),
            [filled["post_type_uuid"]]
        )
        existing_tags = cur.fetchall()
        trimmed_tags = [tag.strip() for tag in filled["tags"].split(",")]
        matched_tags = [tag[0] for tag in existing_tags if tag[2] in trimmed_tags]
        new_tags = [tag for tag in trimmed_tags if tag not in
                    [existing_tag[2] for existing_tag in existing_tags]]
        if len(new_tags) > 0:
            for new_tag in new_tags:
                if len(new_tag) == 0:
                    continue
                slug = re.sub("\s+", "-", new_tag.strip())
                new_uuid = str(uuid.uuid4())
                try:
                    cur.execute(
                        sql.SQL("""INSERT INTO sloth_taxonomy (uuid, slug, display_name, post_type, taxonomy_type) 
                                    VALUES (%s, %s, %s, %s, 'tag');"""),
                        [new_uuid, slug, new_tag, filled["post_type_uuid"]]
                    )
                    matched_tags.append(new_uuid)
                except Exception as e:
                    print(e)
            connection.commit()
        # get user
        author = request.headers.get('authorization').split(":")[1]
        publish_date = -1
        if filled["post_status"] == 'published' and filled["publish_date"] is None:
            publish_date = str(time() * 1000)
        elif filled["post_status"] == 'scheduled':
            publish_date = filled["publish_date"]  # TODO scheduling
        else:
            publish_date = None
        # save post
        if filled["new"]:
            unique_post = False
            while filled["new"] and not unique_post:
                cur.execute(
                    sql.SQL("SELECT count(uuid) FROM sloth_posts WHERE uuid = %s"),
                    [filled["uuid"]]
                )
                if cur.fetchone()[0] != 0:
                    filled["uuid"] = str(uuid.uuid4())
                else:
                    unique_post = True

            cur.execute(
                sql.SQL("SELECT count(slug) FROM sloth_posts WHERE slug LIKE %s OR slug LIKE %s AND post_type=%s;"),
                [f"{filled['slug']}-%", f"{filled['slug']}%", filled["post_type_uuid"]]
            )
            similar = cur.fetchone()[0]
            if int(similar) > 0:
                filled['slug'] = f"{filled['slug']}-{str(int(similar) + 1)}"

            if "lang" not in filled:
                cur.execute(
                    sql.SQL("SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language';"),
                )
                lang = cur.fetchone()[0]
            else:
                lang = filled["lang"]

            cur.execute(
                sql.SQL("""INSERT INTO sloth_posts (uuid, slug, post_type, author, 
                title, content, excerpt, css, js, thumbnail, publish_date, update_date, post_status, lang, password,
                original_lang_entry_uuid) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""),
                [filled["uuid"], filled["slug"], filled["post_type_uuid"], author, filled["title"], filled["content"],
                 filled["excerpt"], filled["css"], filled["js"], filled["thumbnail"], publish_date, str(time() * 1000),
                 filled["post_status"], lang, filled["password"] if "password" in filled else None,
                 filled["original_post"] if "original_post" in filled else ""]
            )
            connection.commit()
            for category in filled["categories"]:
                cur.execute(
                    sql.SQL("""INSERT INTO sloth_post_taxonomies (uuid, post, taxonomy) VALUES (%s, %s, %s)"""),
                    [str(uuid.uuid4()), filled["uuid"], category]
                )
            for tag in matched_tags:
                cur.execute(
                    sql.SQL("""INSERT INTO sloth_post_taxonomies (uuid, post, taxonomy) VALUES (%s, %s, %s)"""),
                    [str(uuid.uuid4()), filled["uuid"], tag]
                )
            result["uuid"] = filled["uuid"]
        else:
            cur.execute(
                sql.SQL("""UPDATE sloth_posts SET slug = %s, title = %s, content = %s, excerpt = %s, css = %s, js = %s,
                 thumbnail = %s, publish_date = %s, update_date = %s, post_status = %s, import_approved = %s,
                 password = %s WHERE uuid = %s;"""),
                [filled["slug"], filled["title"], filled["content"], filled["excerpt"], filled["css"], filled["js"],
                 filled["thumbnail"] if filled["thumbnail"] != "None" else None,
                 filled["publish_date"] if filled["publish_date"] is not None else publish_date,
                 str(time() * 1000), filled["post_status"], filled["approved"],
                 filled["password"] if "password" in filled else None, filled["uuid"]]
            )
            connection.commit()
            cur.execute(
                sql.SQL("""DELETE FROM sloth_post_taxonomies WHERE post = %s;"""),
                [filled["uuid"]]
            )
            for category in filled["categories"]:
                cur.execute(
                    sql.SQL("""INSERT INTO sloth_post_taxonomies (uuid, post, taxonomy) VALUES (%s, %s, %s)"""),
                    [str(uuid.uuid4()), filled["uuid"], category]
                )
            for tag in matched_tags:
                cur.execute(
                    sql.SQL("""INSERT INTO sloth_post_taxonomies (uuid, post, taxonomy) VALUES (%s, %s, %s)"""),
                    [str(uuid.uuid4()), filled["uuid"], tag]
                )
        connection.commit()

        cur.execute(
            sql.SQL("""SELECT A.uuid, A.original_lang_entry_uuid, A.lang, A.slug, A.post_type, A.author, A.title, A.content, 
                                A.excerpt, A.css, A.use_theme_css, A.js, A.use_theme_js, A.thumbnail, A.publish_date, A.update_date, 
                                A.post_status, A.imported, A.import_approved FROM sloth_posts as A WHERE A.uuid = %s;"""),
            [filled["uuid"]]
        )
        generatable_post = parse_raw_post(cur.fetchone())
        generatable_post["related_posts"] = get_related_posts(post=generatable_post, connection=connection)
        # get post
        if filled["post_status"] == 'published':
            gen = PostGenerator(connection=connection)
            gen.run(post=generatable_post)

        if filled["post_status"] == 'protected':
            # get post type slug
            cur.execute(
                sql.SQL("""SELECT slug FROM sloth_post_types WHERE uuid = %s;"""),
                (generatable_post["post_type"], )
            )
            post_type_slug = cur.fetchone()
            cur.execute(
                sql.SQL("""SELECT uuid, short_name, long_name FROM sloth_language_settings WHERE uuid = %s;"""),
                (generatable_post["lang"],)
            )
            language_raw = cur.fetchone()
            # get post slug
            gen = PostGenerator()
            gen.delete_post_files(
                post_type=post_type_slug[0],
                post=generatable_post["slug"],
                language={
                    "uuid": language_raw[0],
                    "short_name": language_raw[1],
                    "long_name": language_raw[2]
                }
            )
    except Exception as e:
        return json.dumps({"error": str(e)}), 500

    cur.close()

    result["saved"] = True
    result["postType"] = generatable_post["post_type"]
    return json.dumps(result)


@post.route("/api/post/delete", methods=['POST', 'DELETE'])
@authorize_rest(0)
@db_connection
def delete_post(*args, permission_level, connection, **kwargs):
    if connection is None:
        abort(500)

    filled = json.loads(request.data)

    cur = connection.cursor()
    res = {}
    count = []
    try:
        cur.execute(
            sql.SQL("""SELECT A.post_type, A.slug, spt.slug 
            FROM sloth_posts as A INNER JOIN sloth_post_types spt on A.post_type = spt.uuid WHERE A.uuid = %s"""),
            [filled["post"]]
        )
        res = cur.fetchone()
        cur.execute(
            sql.SQL("DELETE FROM sloth_posts WHERE uuid = %s"),
            [filled["post"]]
        )
        connection.commit()
        cur.execute(
            sql.SQL("SELECT COUNT(uuid) FROM sloth_posts")
        )
        count = cur.fetchone()
    except Exception as e:
        abort(500)
    cur.close()
    gen = PostGenerator(connection=connection)
    if count[0] == 0:
        gen.delete_post_type_post_files({"slug": res[2]})
    else:
        gen.delete_post_files({"slug": res[2]}, {"slug": res[1]})
        gen.run(post_type=res[2])

    return json.dumps(res[0])


@post.route("/api/post/taxonomy/<taxonomy_id>", methods=["DELETE"])
@authorize_rest(0)
@db_connection
def delete_taxonomy(*args, permission_level, connection, taxonomy_id, **kwargs):
    if connection is None:
        abort(500)

    cur = connection.cursor()

    try:
        cur.execute(
            sql.SQL("DELETE FROM sloth_taxonomy WHERE uuid = %s;"),
            [taxonomy_id]
        )
        connection.commit()
    except Exception as e:
        return json.dumps({"error": "db"})
    cur.close()
    connection.close()
    return json.dumps({"deleted": True})


@post.route("/api/post/regenerate-all", methods=["POST", "PUT"])
@authorize_rest(0)
@db_connection
def regenerate_all(*args, permission_level, connection, **kwargs):
    if connection is None:
        abort(500)

    gen = PostGenerator(connection=connection)
    gen.run()

    return json.dumps({"generating": True})


@post.route("/api/post/secret", methods=["POST"])
@db_connection
def get_protected_post(*args, connection, **kwargs):
    filled = json.loads(request.data)

    raw_post = []

    try:
        cur = connection.cursor()
        cur.execute(
            sql.SQL("""SELECT uuid 
            FROM sloth_posts WHERE password = %s AND slug = %s;"""),
            [filled["password"], filled["slug"]]
        )
        raw_post = cur.fetchone()
    except Exception as e:
        print(e)

    if len(raw_post) != 1:
        return json.dumps({"unauthorized": True}), 401

    gen = PostGenerator(connection=connection)
    protected_post = gen.get_protected_post(uuid=raw_post[0])

    if type(protected_post) is str:
        return json.dumps({
            "content": protected_post
        }), 200
    else:
        return json.dumps(protected_post), 200
