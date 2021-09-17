import datetime
import json
import os
import traceback
import uuid
from pathlib import Path
from time import time
from typing import List, Dict
import threading

import psycopg
from flask import request, current_app, abort, redirect, render_template
from psycopg2 import sql

from app.authorization.authorize import authorize_rest, authorize_web
from app.post import post, get_translations
from app.post.post_generator import PostGenerator
from app.post.post_types import PostTypes
from app.toes.hooks import Hooks, HooksList
from app.toes.toes import render_toe_from_path
from app.utilities import get_languages, get_default_language, parse_raw_post, get_related_posts, get_connection_dict
from app.utilities.db_connection import db_connection_legacy, db_connection
from app.media.routes import get_media
# import toes


@post.route("/post/nothing")
@authorize_web(0)
@db_connection
def no_post(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
    """
    Renders placeholder page when there's no post to edit

    :param args:
    :param permission_level:
    :param connection:
    :param kwargs:
    :return:
    """
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    default_lang = get_default_language(connection=connection)
    return render_template("no-post.html",
                           post_types=post_types_result,
                           permission_level=permission_level,
                           default_lang=default_lang
                           )


@post.route("/post/<post_type>")
@authorize_web(0)
@db_connection
def show_posts_list(*args, permission_level: int, connection: psycopg.Connection, post_type: str, **kwargs):
    """
    

    :param args:
    :param permission_level:
    :param connection:
    :param post_type:
    :param kwargs:
    :return:
    """
    lang_id = ""
    try:
        with connection.cursor() as cur:
            cur.execute("""SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language';""")
            lang_id = cur.fetchone()[0]
    except Exception as e:
        print(e)
        connection.close()
        abort(500)

    return return_post_list(permission_level=permission_level, connection=connection, post_type=post_type,
                            lang_id=lang_id)


@post.route("/post/<post_type>/<lang_id>")
@authorize_web(0)
@db_connection_legacy
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
    # List of {{post_type["name"]}}
    post_type_display_name = [post_type_full for post_type_full in post_types_result if post_type_full['uuid'] == post_type][0]['display_name']
    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="post-list.toe.html",
        hooks=Hooks(),
        data={
            "title": f"List of {post_type_display_name}",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "default_lang": default_lang,
            "hook_list": HooksList.list(),
            "current_lang": current_lang,
            "languages": languages,
            "post_list": items,
            "post_type": post_type_info,
        }
    )


@post.route("/post/<post_id>/edit")
@authorize_web(0)
@db_connection_legacy
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

        media_data = get_media(connection=connection)

        cur.execute(
            sql.SQL("""SELECT sp.title, sp.slug, sp.css, sp.use_theme_css, sp.js, sp.use_theme_js,
             sp.thumbnail, sp.publish_date, sp.update_date, sp.post_status, B.display_name, sp.post_type, sp.imported, 
             sp.import_approved, sp.password, sp.lang, sp.original_lang_entry_uuid, spf.uuid, spf.slug, spf.display_name,
             sp.meta_description, sp.twitter_description
                    FROM sloth_posts AS sp 
                    INNER JOIN sloth_users AS B ON sp.author = B.uuid 
                    INNER JOIN sloth_post_formats spf on spf.uuid = sp.post_format
                    WHERE sp.uuid = %s"""),
            (post_id, )
        )
        raw_post = cur.fetchone()
        if raw_post is None:
            return redirect('/post/nothing')
        cur.execute(
            sql.SQL("SELECT display_name FROM sloth_post_types WHERE uuid = %s"),
            (raw_post[11], )
        )
        post_type_name = cur.fetchone()[0]

        cur.execute(
            sql.SQL("""SELECT uuid, display_name, taxonomy_type, slug FROM sloth_taxonomy
                                WHERE post_type = %s AND lang = %s"""),
            (raw_post[11], raw_post[15])
        )
        raw_all_taxonomies = cur.fetchall()
        cur.execute(
            sql.SQL("""SELECT taxonomy FROM sloth_post_taxonomies
                                        WHERE post = %s"""),
            (post_id,)
        )
        raw_post_taxonomies = cur.fetchall()
        cur.execute(
            sql.SQL("SELECT unnest(enum_range(NULL::sloth_post_status))")
        )
        temp_post_statuses = cur.fetchall()
        if raw_post[6] is not None:
            cur.execute(
                sql.SQL(
                    """SELECT sma.alt, 
                    concat(
                        (SELECT settings_value FROM sloth_settings WHERE settings_name = 'site_url'), '/',file_path
                    )
                        FROM sloth_media AS sm 
                        INNER JOIN sloth_media_alts sma on sm.uuid = sma.media
                        WHERE sm.uuid=%s AND sma.lang = %s"""),
                (raw_post[6], raw_post[15])
            )
            temp_thumbnail_info = cur.fetchone()
        current_lang, languages = get_languages(connection=connection, lang_id=raw_post[15])
        translatable = []

        if raw_post[16]:
            translations, translatable = get_translations(
                connection=connection,
                post_uuid="",
                original_entry_uuid=raw_post[16],
                languages=languages
            )
        else:
            translations, translatable = get_translations(
                connection=connection,
                post_uuid="",
                original_entry_uuid=post_id,
                languages=languages
            )
        cur.execute(
            sql.SQL(
                """SELECT uuid, slug, display_name FROM sloth_post_formats WHERE post_type = %s"""
            ),
            (raw_post[11],)
        )
        post_formats = [{
            "uuid": pf[0],
            "slug": pf[1],
            "display_name": pf[2]
        } for pf in cur.fetchall()]

        cur.execute(
            sql.SQL(
                """SELECT uuid, name, version, location 
                FROM sloth_libraries;""")
        )
        libs = [{
            "uuid": lib[0],
            "name": lib[1],
            "version": lib[2],
            "location": lib[3]
        } for lib in cur.fetchall()]
        cur.execute(
            sql.SQL(
                """SELECT sl.uuid, sl.name, sl.version, spl.hook_name
                FROM sloth_post_libraries AS spl
                INNER JOIN sloth_libraries sl on spl.library = sl.uuid
                WHERE spl.post = %s;"""
            ),
            (post_id,)
        )
        post_libs = [{
            "uuid": lib[0],
            "name": lib[1],
            "version": lib[2],
            "hook": lib[3]
        } for lib in cur.fetchall()]
        cur.execute(
            sql.SQL(
                """SELECT content, section_type, position
                FROM sloth_post_sections
                WHERE post = %s
                ORDER BY position ASC;"""
            ),
            (post_id,)
        )
        sections = [{
            "content": section[0],
            "type": section[1],
            "position": section[2]
        } for section in cur.fetchall()]

        if raw_post[16]:
            cur.execute(
                sql.SQL(
                    """SELECT content, section_type, position
                    FROM sloth_post_sections
                    WHERE post = %s
                    ORDER BY position ASC;"""
                ),
                (raw_post[16],)
            )
            translated_sections = cur.fetchall()
            while len(sections) < len(translated_sections):
                sections.append({
                    "content": "",
                    "original": "",
                    "type": translated_sections[len(sections)][1],
                    "position": len(sections)
                })
            for section in sections:
                for trans_section in translated_sections:
                    if section["position"] == trans_section[2]:
                        section["original"] = trans_section[0]

        sections = json.dumps(sections)
    except Exception as e:
        print(traceback.format_exc())
        print("db error B")
        print(e)
        abort(500)

    cur.close()
    default_lang = get_default_language(connection=connection)
    connection.close()

    token = request.cookies.get('sloth_session')

    publish_datetime = datetime.datetime.fromtimestamp(raw_post[7] / 1000) if raw_post[7] else None

    categories, tags = separate_taxonomies(taxonomies=raw_all_taxonomies, post_taxonomies=raw_post_taxonomies)

    data = {
        "uuid": post_id,
        "title": raw_post[0],
        "slug": raw_post[1],
        "sections": sections,
        "css": raw_post[2],
        "use_theme_css": raw_post[3],
        "js": raw_post[4],
        "use_theme_js": raw_post[5],
        "thumbnail_path": temp_thumbnail_info[1] if len(temp_thumbnail_info) >= 2 else None,
        "thumbnail_uuid": raw_post[8] if raw_post[6] is not None else "",
        "thumbnail_alt": temp_thumbnail_info[0] if len(temp_thumbnail_info) > 0 else None,
        "publish_date": publish_datetime.strftime("%Y-%m-%d") if publish_datetime else None,
        "publish_time": publish_datetime.strftime("%H:%M") if publish_datetime else None,
        "update_date": raw_post[8],
        "status": raw_post[9],
        "display_name": raw_post[10],
        "post_type": raw_post[11],
        "imported": raw_post[12],
        "approved": raw_post[13],
        "password": raw_post[14],
        "lang": raw_post[15],
        "categories": categories,
        "tags": tags,
        "format_uuid": raw_post[17],
        "format_slug": raw_post[18],
        "format_name": raw_post[19],
        "meta_description": raw_post[20],
        "social_description": raw_post[21],
        "libraries": post_libs,
        "original_post": raw_post[16]
    }
    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="post-edit.toe.html",
        hooks=Hooks(),
        data={
            "title": f"Add new {post_type_name}" if "new" in data else f"Edit {post_type_name}",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "token": token,
            "post_type_name": post_type_name,
            "data": data,
            "media": media,
            "post_statuses": [item for sublist in temp_post_statuses for item in sublist],
            "default_lang": default_lang,
            "languages": translatable,
            "translations": translations,
            "current_lang_id": data["lang"],
            "post_formats": post_formats,
            "libs": libs,
            "hook_list": HooksList.list(),
            "media_data": media_data
        }
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
            "selected": True if raw_taxonomy[0] in flat_post_taxonomies else False,
            "slug": raw_taxonomy[3]
        }
        if taxonomy["type"] == 'category':
            categories.append(taxonomy)
        elif taxonomy["type"] == 'tag':
            tags.append(taxonomy)

    return categories, tags


@post.route("/post/<post_type>/new/<lang_id>")
@authorize_web(0)
@db_connection_legacy
def show_post_new(*args, permission_level, connection, post_type, lang_id, **kwargs):
    original_post = request.args.get('original');
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    cur = connection.cursor()
    media = []
    post_type_name = ""
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
            sql.SQL("""SELECT uuid, display_name, taxonomy_type, slug FROM sloth_taxonomy
                                        WHERE post_type = %s AND lang = %s"""),
            (post_type, lang_id)
        )
        raw_all_taxonomies = cur.fetchall()
        current_lang, languages = get_languages(connection=connection, lang_id=lang_id)
        default_lang = get_default_language(connection=connection)
        sections = []
        if original_post:
            translations, translatable_languages = get_translations(
                connection=connection,
                post_uuid="",
                original_entry_uuid=original_post,
                languages=languages
            )
            cur.execute(
                sql.SQL(
                    """SELECT content, section_type, position
                    FROM sloth_post_sections
                    WHERE post = %s
                    ORDER BY position ASC;"""
                ),
                (original_post,)
            )
            sections = [{
                "content": "",
                "original": section[0],
                "type": section[1],
                "position": section[2],
            } for section in cur.fetchall()]
        else:
            translatable_languages = languages
            translations = []
        cur.execute(
            sql.SQL(
                """SELECT uuid, slug, display_name FROM sloth_post_formats WHERE post_type = %s"""
            ),
            (post_type,)
        )
        post_formats = [{
            "uuid": pf[0],
            "slug": pf[1],
            "display_name": pf[2]
        } for pf in cur.fetchall()]

        cur.execute(
            sql.SQL(
                """SELECT uuid FROM sloth_post_formats WHERE post_type = %s AND deletable = %s """
            ),
            (post_type, False)
        )
        default_format = cur.fetchone()[0]

        cur.execute(
            sql.SQL(
                """SELECT uuid, name, version, location 
                FROM sloth_libraries;""")
        )
        libs = [{
            "uuid": lib[0],
            "name": lib[1],
            "version": lib[2],
            "location": lib[3]
        } for lib in cur.fetchall()]
        post_libs = []
    except Exception as e:
        print("db error A")
        abort(500)

    cur.close()
    connection.close()

    categories, tags = separate_taxonomies(taxonomies=raw_all_taxonomies, post_taxonomies=[])
    sections = json.dumps(sections)
    data = {
        "new": True,
        "use_theme_js": True,
        "use_theme_css": True,
        "status": "draft",
        "uuid": uuid.uuid4(),
        "post_type": post_type,
        "lang": lang_id,
        "original_post": original_post,
        "format_uuid": default_format,
        "libraries": post_libs,
        "categories": categories,
        "tags": tags,
        "sections": sections,
    }

    token = request.cookies.get('sloth_session')

    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="post-edit.toe.html",
        hooks=Hooks(),
        data={
            "title": f"Add new {post_type_name}" if data["new"] else f"Edit {post_type_name}",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "token": token,
            "post_type_name": post_type_name,
            "data": data,
            "media": media,
            "post_statuses": [item for sublist in temp_post_statuses for item in sublist],
            "default_lang": default_lang,
            "languages": translatable_languages,
            "translations": translations,
            "current_lang_id": data["lang"],
            "post_formats": post_formats,
            "libs": libs,
            "hook_list": HooksList.list()
        }
    )


@post.route("/post/<type_id>/taxonomy")
@authorize_web(0)
@db_connection_legacy
def show_post_taxonomy_main_lang(*args, permission_level, connection, type_id, **kwargs):
    return show_taxonomy(
        permission_level=permission_level,
        connection=connection,
        type_id=type_id,
        lang_id=get_default_language(connection=connection)["uuid"]
    )


@post.route("/post/<type_id>/taxonomy/<lang_id>")
@authorize_web(0)
@db_connection_legacy
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


@post.route("/post/<type_id>/formats")
@authorize_web(0)
@db_connection_legacy
def show_formats(*args, permission_level, connection, type_id, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    lang_id = get_default_language(connection=connection)["uuid"]

    cur = connection.cursor()
    taxonomy = {}
    try:
        cur.execute(
            sql.SQL(
                """SELECT uuid, slug, display_name, deletable
                 FROM sloth_post_formats
                 WHERE post_type = %s"""
            ),
            (type_id,)
        )
        post_formats = [{
            "uuid": pt[0],
            "slug": pt[1],
            "display_name": pt[2],
            "deletable": pt[3]
        } for pt in cur.fetchall()]
    except Exception as e:
        print("db error C")
        abort(500)

    cur.close()
    # current_lang, languages = get_languages(connection=connection, lang_id=lang_id)
    default_language = get_default_language(connection=connection)
    current_lang, languages = get_languages(connection=connection, lang_id=lang_id)

    connection.close()

    return render_toe_from_path(
        template="formats-list.toe.html",
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        data={
            "title": "List of formats",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "post_formats": post_formats,
            "post_type_uuid": type_id,
            "default_lang": default_language,
            "languages": languages
        },
        hooks=Hooks()
    )


@post.route("/api/post/formats", methods=["POST", "PUT"])
@authorize_web(0)
@db_connection_legacy
def save_post_format(*args, permission_level, connection, **kwargs):
    filled = json.loads(request.data)
    cur = connection.cursor()
    slug_changed = False
    try:
        if filled['uuid'] != 'new':
            cur.execute(
                sql.SQL("""SELECT slug FROM sloth_post_formats WHERE uuid = %s;"""),
                (filled["uuid"],)
            )
            old_slug = cur.fetchone()[0]
            if filled['slug'] != old_slug:
                slug_changed = True

        if slug_changed or filled['uuid'] == 'new':
            cur.execute(
                sql.SQL(
                    """SELECT count(slug) FROM sloth_post_formats 
                    WHERE slug LIKE %s OR slug LIKE %s AND post_type=%s;"""
                ),
                (f"{filled['slug']}-%", f"{filled['slug']}%", filled["post_type_uuid"])
            )
            similar = cur.fetchone()[0]
            if int(similar) > 0:
                filled['slug'] = f"{filled['slug']}-{str(int(similar) + 1)}"

        if filled['uuid'] == 'new':
            cur.execute(
                sql.SQL(
                    """INSERT INTO sloth_post_formats (uuid, slug, display_name, post_type, deletable) 
                    VALUES (%s, %s, %s, %s, %s) RETURNING uuid, slug, display_name, deletable;"""
                ),
                (str(uuid.uuid4()), filled['slug'], filled["display_name"], filled["post_type_uuid"], True)
            )
        else:
            cur.execute(
                sql.SQL(
                    """UPDATE sloth_post_formats SET slug = %s, display_name = %s 
                    WHERE uuid = %s RETURNING uuid, slug, display_name, deletable;"""
                ),
                (filled['slug'], filled["display_name"], filled["uuid"])
            )
        raw_result = cur.fetchone()
        connection.commit()
    except Exception as e:
        print("db error C")
        abort(500)

    cur.close()
    connection.close()

    return json.dumps({
        "uuid": raw_result[0],
        "display_name": raw_result[2],
        "slug": raw_result[1],
        "deletable": raw_result[3]
    }), 200


@post.route("/api/post/formats", methods=["DELETE"])
@authorize_web(0)
@db_connection_legacy
def delete_post_format(*args, permission_level, connection, **kwargs):
    filled = json.loads(request.data)
    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL(
                """DELETE FROM sloth_post_formats
                 WHERE uuid = %s AND deletable = %s"""
            ),
            (filled["uuid"], True)
        )
        connection.commit()
        cur.execute(
            sql.SQL(
                """SELECT uuid FROM sloth_post_formats
                 WHERE uuid = %s"""
            ),
            (filled["uuid"],)
        )
        if len(cur.fetchall()) > 0:
            cur.close()
            connection.close()
            return json.dumps({
                "uuid": filled["uuid"],
                "deleted": False
            }), 406
    except Exception as e:
        print("db error C")
        abort(500)

    cur.close()
    connection.close()

    return json.dumps({
        "uuid": filled["uuid"],
        "deleted": True
    }), 204


@post.route("/post/<type_id>/taxonomy/<taxonomy_type>/<taxonomy_id>", methods=["GET"])
@authorize_web(0)
@db_connection_legacy
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
@db_connection_legacy
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
@db_connection_legacy
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
@db_connection_legacy
def get_media_data(*args, connection, lang_id: str, **kwargs):
    if connection is None:
        abort(500)

    cur = connection.cursor()
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
@db_connection_legacy
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
            sql.SQL("INSERT INTO sloth_media VALUES (%s, %s, %s) RETURNING uuid, file_path"),
            [str(uuid.uuid4()), os.path.join("sloth-content", file_name), ""]
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
@db_connection_legacy
def save_post(*args, connection=None, **kwargs):
    if connection is None:
        abort(500)
    result = {}
    filled = json.loads(request.data)
    filled["thumbnail"] = filled["thumbnail"] if len(filled["thumbnail"]) > 0 else None
    cur = connection.cursor()
    if "lang" not in filled:
        cur.execute(
            sql.SQL("SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language';"),
        )
        lang = cur.fetchone()[0]
    else:
        lang = filled["lang"]
    try:
        # process tags
        cur.execute(
            sql.SQL(
                """SELECT uuid, slug, display_name, post_type, taxonomy_type 
                    FROM sloth_taxonomy 
                    WHERE post_type = %s AND taxonomy_type = 'tag' AND lang = %s;"""
            ),
            (filled["post_type_uuid"], lang)
        )
        existing_tags = cur.fetchall()

        existing_tags_slugs = [slug[1] for slug in existing_tags]
        # refactoring candidate:
        matched_tags = []
        new_tags = []
        for tag in filled["tags"]:
            if tag["slug"] in existing_tags_slugs:
                if tag["uuid"] == "added":
                    for et in existing_tags:
                        if et[1] == tag["slug"]:
                            tag["uuid"] = et[0]
                            break
                matched_tags.append(tag)
            else:
                tag["uuid"] = str(uuid.uuid4())
                new_tags.append(tag)

        for new_tag in new_tags:
            cur.execute(
                sql.SQL("""INSERT INTO sloth_taxonomy (uuid, slug, display_name, post_type, taxonomy_type, lang) 
                            VALUES (%s, %s, %s, %s, 'tag', %s);"""),
                (new_tag["uuid"], new_tag["slug"], new_tag["displayName"], filled["post_type_uuid"],
                 filled["lang"])
            )
            matched_tags.append(new_tag)

        connection.commit()
        # get user
        author = request.headers.get('authorization').split(":")[1]

        if filled["post_status"] == 'published' and filled["publish_date"] is None:
            publish_date = str(time() * 1000)
        elif filled["post_status"] == 'scheduled':
            publish_date = filled["publish_date"]
        elif filled['post_status'] == 'draft':
            publish_date = None
        # save post
        if filled["new"] and str(filled["new"]).lower() != 'none':
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

            cur.execute(
                sql.SQL("""INSERT INTO sloth_posts (uuid, slug, post_type, author, 
                title, css, js, thumbnail, publish_date, update_date, post_status, lang, password,
                original_lang_entry_uuid, post_format, meta_description, twitter_description) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""),
                (filled["uuid"], filled["slug"], filled["post_type_uuid"], author, filled["title"],
                 filled["css"], filled["js"], filled["thumbnail"], publish_date, str(time() * 1000),
                 filled["post_status"], lang, filled["password"] if "password" in filled else None,
                 filled["original_post"] if "original_post" in filled else "", filled["post_format"],
                 filled["meta_description"], filled["social_description"])
            )
            connection.commit()
            taxonomy_to_clean = sort_out_post_taxonomies(connection=connection, article=filled, tags=matched_tags)
            result["uuid"] = filled["uuid"]
        else:
            # when editting this don't forget that last item needs to be uuid
            cur.execute(
                sql.SQL("""UPDATE sloth_posts SET slug = %s, title = %s, css = %s, js = %s,
                 thumbnail = %s, publish_date = %s, update_date = %s, post_status = %s, import_approved = %s,
                 password = %s, post_format = %s, meta_description = %s, twitter_description = %s WHERE uuid = %s;"""),
                (filled["slug"], filled["title"], filled["css"], filled["js"],
                 filled["thumbnail"] if filled["thumbnail"] != "None" else None,
                 filled["publish_date"] if filled["publish_date"] is not None else publish_date,
                 str(time() * 1000), filled["post_status"], filled["approved"],
                 filled["password"] if "password" in filled else None, filled["post_format"],
                 filled["meta_description"], filled["social_description"], filled["uuid"])
            )
            connection.commit()
            taxonomy_to_clean = sort_out_post_taxonomies(connection=connection, article=filled, tags=matched_tags)

        # save libraries
        cur.execute(
            sql.SQL("""DELETE FROM sloth_post_libraries WHERE post = %s;"""),
            (filled["uuid"],)
        )
        for lib in filled["libs"]:
            cur.execute(
                sql.SQL(
                    """INSERT INTO sloth_post_libraries (uuid, post, library, hook_name)  VALUES (%s, %s, %s, %s)"""),
                (str(uuid.uuid4()), filled["uuid"], lib["libId"], lib["hook"])
            )
        connection.commit()

        cur.execute(
            sql.SQL("""DELETE from sloth_post_sections WHERE post = %s;"""),
            (filled["uuid"],)
        )
        for section in filled["sections"]:
            cur.execute(
                sql.SQL("""INSERT INTO sloth_post_sections VALUES (%s, %s, %s, %s, %s)"""),
                (str(uuid.uuid4()), filled["uuid"], section["content"], section["type"], section["position"])
            )
        connection.commit()

        cur.execute(
            sql.SQL("""SELECT sp.uuid, sp.original_lang_entry_uuid, sp.lang, sp.slug, sp.post_type, sp.author, sp.title, 
                                sp.css, sp.use_theme_css, sp.js, sp.use_theme_js, sp.thumbnail, sp.publish_date, sp.update_date, 
                                sp.post_status, sp.imported, sp.import_approved, sp.meta_description, 
                                sp.twitter_description, spf.uuid, spf.slug, spf.display_name
                                FROM sloth_posts as sp 
                                INNER JOIN sloth_post_formats spf on spf.uuid = sp.post_format
                                WHERE sp.uuid = %s;"""),
            (filled["uuid"],)
        )
        saved_post = cur.fetchone()
        cur.execute(
            sql.SQL(
                """SELECT content, section_type, position
                FROM sloth_post_sections
                WHERE post = %s
                ORDER BY position ASC;"""
            ),
            (filled["uuid"],)
        )
        sections = [{
            "content": section[0],
            "type": section[1],
            "position": section[2]
        } for section in cur.fetchall()]

        generatable_post = parse_raw_post(saved_post, sections=sections)
        cur.execute(
            sql.SQL(
                """SELECT sl.location, spl.hook_name
                FROM sloth_post_libraries AS spl
                INNER JOIN sloth_libraries sl on sl.uuid = spl.library
                WHERE spl.post = %s;"""
            ),
            (filled["uuid"],)
        )
        generatable_post["libraries"] = [{
            "location": lib[0],
            "hook_name": lib[1]
        } for lib in cur.fetchall()]
        generatable_post["related_posts"] = get_related_posts(post=generatable_post, connection=connection)
        # get post
        if filled["post_status"] == 'published':
            gen = PostGenerator(connection=connection)
            gen.run(post=generatable_post, regenerate_taxonomies=taxonomy_to_clean)
            # (threading.Thread(
            #     target=toes.generate_post,
            #     args=[
            #         get_connection_dict(current_app.config),
            #         os.getcwd(),
            #         generatable_post,
            #         current_app.config["THEMES_PATH"],
            #         current_app.config["OUTPUT_PATH"],
            #         taxonomy_to_clean
            #     ]
            # )).start()

        if filled["post_status"] == 'protected':
            # get post type slug
            cur.execute(
                sql.SQL("""SELECT slug FROM sloth_post_types WHERE uuid = %s;"""),
                (generatable_post["post_type"],)
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
        print(traceback.format_exc())
        return json.dumps({"error": str(e)}), 500

    cur.close()

    result["saved"] = True
    result["postType"] = generatable_post["post_type"]
    return json.dumps(result)


def sort_out_post_taxonomies(*args, connection, article, tags, **kwargs):
    cur = connection.cursor()
    categories = article["categories"]
    cur.execute(
        sql.SQL("""SELECT uuid, taxonomy FROM sloth_post_taxonomies WHERE post = %s;"""),
        (article["uuid"],)
    )
    raw_taxonomies = cur.fetchall()
    taxonomies = [{
        "uuid": taxonomy[0],
        "taxonomy": taxonomy[1]
    } for taxonomy in raw_taxonomies]
    for_deletion = []
    tag_ids = [tag["uuid"] for tag in tags]
    for taxonomy in taxonomies:
        if taxonomy["taxonomy"] not in categories and taxonomy["taxonomy"] not in tag_ids:
            for_deletion.append(taxonomy)
        elif taxonomy["taxonomy"] in categories:
            categories.remove(taxonomy["taxonomy"])
        elif taxonomy["taxonomy"] in tag_ids:
            tags = [tag for tag in tags if tag["uuid"] != taxonomy["taxonomy"]]

    for taxonomy in for_deletion:
        cur.execute(
            sql.SQL("""DELETE FROM sloth_post_taxonomies WHERE uuid = %s"""),
            (taxonomy["uuid"],)
        )
        taxonomies.remove(taxonomy)
    connection.commit()

    for category in categories:
        cur.execute(
            sql.SQL("""INSERT INTO sloth_post_taxonomies (uuid, post, taxonomy) VALUES (%s, %s, %s)"""),
            (str(uuid.uuid4()), article["uuid"], category)
        )
    for tag in tags:
        cur.execute(
            sql.SQL("""INSERT INTO sloth_post_taxonomies (uuid, post, taxonomy) VALUES (%s, %s, %s)"""),
            (str(uuid.uuid4()), article["uuid"], tag["uuid"])
        )
    connection.commit()
    cur.close()

    return for_deletion


@post.route("/api/post/delete", methods=['POST', 'DELETE'])
@authorize_rest(0)
@db_connection_legacy
def delete_post(*args, permission_level, connection, **kwargs):
    if connection is None:
        abort(500)

    filled = json.loads(request.data)

    cur = connection.cursor()
    res = {}
    count = []
    try:
        cur.execute(
            sql.SQL("""SELECT A.post_type, A.slug, spt.slug, A.lang 
            FROM sloth_posts as A INNER JOIN sloth_post_types spt on A.post_type = spt.uuid WHERE A.uuid = %s"""),
            (filled["post"], )
        )
        res = cur.fetchone()
        cur.execute(
            sql.SQL("""SELECT A.uuid 
                    FROM sloth_posts as A WHERE A.original_lang_entry_uuid = %s ORDER BY publish_date ASC"""),
            (filled["post"],)
        )
        oldest_alternative = cur.fetchone()
        cur.execute(
            sql.SQL("""UPDATE sloth_posts SET original_lang_entry_uuid = '' WHERE uuid = %s;"""),
            oldest_alternative
        )
        cur.execute(
            sql.SQL("""UPDATE sloth_posts SET original_lang_entry_uuid = %s WHERE original_lang_entry_uuid = %s;"""),
            (oldest_alternative[0], filled["post"])
        )
        cur.execute(
            sql.SQL("""DELETE FROM sloth_post_taxonomies WHERE post = %s;"""),
            (filled["post"],)
        )
        cur.execute(
            sql.SQL("""DELETE FROM sloth_post_sections WHERE post = %s;"""),
            (filled["post"],)
        )
        cur.execute(
            sql.SQL("DELETE FROM sloth_posts WHERE uuid = %s"),
            (filled["post"],)
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
        # post_type, language,
        gen.delete_post_type_post_files(post_type=res[2], language=res[3])
    else:
        # post_type, post, language,
        gen.delete_post_files(post_type=res[2], post=res[1], language=res[3])
        gen.run(post_type=res[2])

    return json.dumps(res[0])


@post.route("/api/post/taxonomy/<taxonomy_id>", methods=["DELETE"])
@authorize_rest(0)
@db_connection_legacy
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
@db_connection_legacy
def regenerate_all(*args, permission_level, connection, **kwargs):
    if connection is None:
        abort(500)

    gen = PostGenerator(connection=connection)
    gen.run()

    return json.dumps({"generating": True})


@post.route("/api/post/secret", methods=["POST"])
@db_connection_legacy
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


@post.route("/api/post/is-generating", methods=["GET"])
@authorize_rest(0)
def is_generating(*args, permission_level, **kwargs):
    return json.dumps({
        "generating": Path(os.path.join(os.getcwd(), 'generating.lock')).is_file()
    })
