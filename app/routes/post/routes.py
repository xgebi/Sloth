from __future__ import annotations

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
from flask import request, current_app, abort, redirect, render_template, escape

from app.authorization.authorize import authorize_rest, authorize_web
from app.routes.post import post
from app.services.post_services import get_translations
from app.back_office.post.post_generator import PostGenerator
from app.back_office.post.post_types import PostTypes
from app.toes.hooks import Hooks, HooksList
from app.toes.toes import render_toe_from_path
from app.utilities.utilities import get_languages, get_default_language, get_related_posts, prepare_description
from app.utilities.db_connection import db_connection
from app.media.routes import get_media
from app.back_office.post.post_query_builder import build_post_query, normalize_post_from_query


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
    Renders a list of posts for default language

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


@post.route("/api/post/<post_type>/<language>")
@authorize_rest(0)
@db_connection
def get_posts_list(*args, permission_level: int, connection: psycopg.Connection, post_type: str, language: str,
                   **kwargs):
    """
    Gets a list of posts for default language

    :param args:
    :param permission_level:
    :param connection:
    :param post_type:
    :param language:
    :param kwargs:
    :return:
    """
    try:
        with connection.cursor() as cur:
            cur.execute("""SELECT A.uuid, A.title, A.publish_date, A.update_date, A.post_status, A.post_type,
                            A.lang
                            FROM sloth_posts AS A 
                            WHERE A.post_type = %s AND A.lang = %s ORDER BY A.update_date DESC""",
                        (post_type, language))
            raw_items = cur.fetchall()
            return json.dumps([{
                "uuid": item[0],
                "title": item[1],
                "publishDate": item[2],
                "updateDate": item[3],
                "postStatus": item[4],
                "postType": item[5],
                "language": item[6],
            } for item in raw_items])
    except Exception as e:
        print(e)
        connection.close()
        abort(500)


@post.route("/post/<post_type>/<lang_id>")
@authorize_web(0)
@db_connection
def show_posts_list_language(*args, permission_level: int, connection: psycopg.Connection, post_type: str, lang_id: str,
                             **kwargs):
    """
    Renders list of post for a language

    :param args:
    :param permission_level:
    :param connection:
    :param post_type:
    :param lang_id:
    :param kwargs:
    :return:
    """
    return return_post_list(permission_level=permission_level, connection=connection, post_type=post_type,
                            lang_id=lang_id)


def return_post_list(*args, permission_level: int, connection: psycopg.Connection, post_type: str, lang_id: str,
                     **kwargs):
    """
    Returns rendering of list of posts belonging to a post type

    :param args:
    :param permission_level:
    :param connection:
    :param post_type:
    :param lang_id:
    :param kwargs:
    :return:
    """

    post_type_info = {
        "uuid": post_type
    }

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    try:
        with connection.cursor() as cur:
            cur.execute("""SELECT display_name FROM sloth_post_types WHERE uuid = %s""", (post_type,))
            res = cur.fetchall()
            post_type_info["name"] = res[0][0]
            cur.execute("""SELECT A.uuid, A.title, A.publish_date, A.update_date, A.post_status, B.display_name 
                FROM sloth_posts AS A INNER JOIN sloth_users AS B ON A.author = B.uuid 
                WHERE A.post_type = %s AND A.lang = %s ORDER BY A.update_date DESC""",
                        (post_type, lang_id))
            raw_items = cur.fetchall()
    except Exception:
        print("db error Q")
        connection.close()
        abort(500)

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
    post_type_display_name = \
        [post_type_full for post_type_full in post_types_result if post_type_full['uuid'] == post_type][0][
            'display_name']
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


@post.route("/api/post/<post_id>/edit")
@authorize_rest(0)
@db_connection
def get_post_edit(*args, permission_level: int, connection: psycopg.Connection, post_id: str, **kwargs):
    """
    Gets data for post_id
    :param args:
    :param permission_level:
    :param connection:
    :param post_id:
    :param kwargs:
    :return:
    """
    post_data, libs, media_data, post_libs, temp_thumbnail_info, categories, tags, post_type_name, temp_post_statuses, translatable, translations, post_formats, post_statuses = get_post_data(
        connection=connection, post_id=post_id)

    return json.dumps(post_data)


@post.route("/post/<post_id>/edit")
@authorize_web(0)
@db_connection
def show_post_edit(*args, permission_level: int, connection: psycopg.Connection, post_id: str, **kwargs):
    """
    Renders an edit page for a post

    :param args:
    :param permission_level:
    :param connection:
    :param post_id:
    :param kwargs:
    :return:
    """

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    post_data, libs, media_data, post_libs, temp_thumbnail_info, categories, tags, post_type_name, temp_post_statuses, translatable, translations, post_formats, post_statuses = get_post_data(
        connection=connection, post_id=post_id)

    default_lang = get_default_language(connection=connection)
    connection.close()

    token = request.cookies.get('sloth_session')

    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="post-edit.toe.html",
        hooks=Hooks(),
        data={
            "title": f"Add new {post_type_name}" if "new" in post_data else f"Edit {post_type_name}",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "token": token,
            "post_type_name": post_type_name,
            "data": post_data,
            "post_statuses": post_statuses,
            "default_lang": default_lang,
            "languages": translatable,
            "translations": translations,
            "current_lang_id": post_data["lang"],
            "post_formats": post_formats,
            "libs": libs,
            "hook_list": HooksList.list(),
            "media_data": [media_data[key] for key in media_data.keys()]
        }
    )


def get_post_data(*args, connection: psycopg.Connection, post_id: str, **kwargs):
    post_type_name = ""
    temp_thumbnail_info = []
    try:
        with connection.cursor() as cur:
            media_data = get_media(connection=connection)
            cur.execute(build_post_query(uuid=True), (post_id,))
            normed_post = normalize_post_from_query(cur.fetchone())
            if normed_post is None:
                return redirect('/post/nothing')
            cur.execute("""SELECT display_name FROM sloth_post_types WHERE uuid = %s""",
                        (normed_post["post_type"],))
            post_type_name = cur.fetchone()[0]

            cur.execute("""SELECT uuid, display_name, taxonomy_type, slug FROM sloth_taxonomy
                                        WHERE post_type = %s AND lang = %s""",
                        (normed_post["post_type"], normed_post["lang"]))
            raw_all_taxonomies = cur.fetchall()
            cur.execute("""SELECT taxonomy FROM sloth_post_taxonomies
                                                WHERE post = %s""",
                        (post_id,))
            raw_post_taxonomies = cur.fetchall()
            cur.execute("""SELECT unnest(enum_range(NULL::sloth_post_status))"""
                        )
            temp_post_statuses = cur.fetchall()
            if normed_post["thumbnail"] is not None:
                cur.execute(
                    """SELECT sma.alt, 
                    concat(
                        (SELECT settings_value FROM sloth_settings WHERE settings_name = 'site_url'), '/',file_path
                    )
                        FROM sloth_media AS sm 
                        INNER JOIN sloth_media_alts sma on sm.uuid = sma.media
                        WHERE sm.uuid=%s AND sma.lang = %s""",
                    (normed_post["thumbnail"], normed_post["lang"]))
                temp_thumbnail_info = cur.fetchone()
            current_lang, languages = get_languages(connection=connection, lang_id=normed_post["lang"])
            translatable = []

            if "original_lang_entry_uuid" in normed_post and normed_post["original_lang_entry_uuid"] is not None and len(normed_post["original_lang_entry_uuid"]) > 0:
                translations, translatable = get_translations(
                    connection=connection,
                    post_uuid=normed_post["uuid"],
                    original_entry_uuid=normed_post["original_lang_entry_uuid"],
                    languages=languages
                )
            else:
                translations, translatable = get_translations(
                    connection=connection,
                    post_uuid="",
                    original_entry_uuid=post_id,
                    languages=languages
                )
            cur.execute("""SELECT uuid, slug, display_name FROM sloth_post_formats WHERE post_type = %s""",
                        (normed_post["post_type"],))
            post_formats = [{
                "uuid": pf[0],
                "slug": pf[1],
                "display_name": pf[2]
            } for pf in cur.fetchall()]

            cur.execute("""SELECT uuid, name, version, location 
                        FROM sloth_libraries;""")
            libs = [{
                "uuid": lib[0],
                "name": lib[1],
                "version": lib[2],
                "location": lib[3]
            } for lib in cur.fetchall()]
            cur.execute("""SELECT sl.uuid, sl.name, sl.version, spl.hook_name
                        FROM sloth_post_libraries AS spl
                        INNER JOIN sloth_libraries sl on spl.library = sl.uuid
                        WHERE spl.post = %s;""",
                        (post_id,))
            post_libs = [{
                "uuid": lib[0],
                "name": lib[1],
                "version": lib[2],
                "hook": lib[3]
            } for lib in cur.fetchall()]
            cur.execute("""SELECT content, section_type, position
                        FROM sloth_post_sections
                        WHERE post = %s
                        ORDER BY position;""",
                        (post_id,))
            sections = [{
                "content": section[0],
                "original": "",
                "type": section[1],
                "position": section[2],
            } for section in cur.fetchall()]

            if normed_post["original_lang_entry_uuid"]:
                cur.execute("""SELECT content, section_type, position
                            FROM sloth_post_sections
                            WHERE post = %s
                            ORDER BY position;""",
                            (normed_post["original_lang_entry_uuid"],))
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
    except Exception as e:
        print(traceback.format_exc())
        print("db error B")
        print(e)
        connection.close()
        abort(500)
    categories, tags = separate_taxonomies(taxonomies=raw_all_taxonomies, post_taxonomies=raw_post_taxonomies)
    post_statuses = [item for sublist in temp_post_statuses for item in sublist]
    normed_post.update({"sections": sections})
    return normed_post, libs, media_data, post_libs, temp_thumbnail_info, categories, tags, post_type_name, temp_post_statuses, translatable, translations, post_formats, post_statuses


def separate_taxonomies(*args, taxonomies: List, post_taxonomies: List, **kwargs) -> (List[Dict], List[Dict]):
    """
    Separates taxonomies to tags and categories

    :param args:
    :param taxonomies:
    :param post_taxonomies:
    :param kwargs:
    :return:
    """
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
@db_connection
def show_post_new(*args, permission_level: int, connection: psycopg.Connection, post_type: str, lang_id: str, **kwargs):
    """
    Renders pages for a new post in a language

    :param args:
    :param permission_level:
    :param connection:
    :param post_type:
    :param lang_id:
    :param kwargs:
    :return:
    """

    data = prepare_data_new_post(connection=connection, post_type=post_type, lang_id=lang_id)
    data["permission_level"] = permission_level
    data["token"] = request.cookies.get('sloth_session')

    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="post-edit.toe.html",
        hooks=Hooks(),
        data=data
    )


@post.route("/api/post/<post_type>/new/<lang_id>")
@authorize_rest(0)
@db_connection
def get_post_new(*args, permission_level: int, connection: psycopg.Connection, post_type: str, lang_id: str, **kwargs):
    """
    Renders pages for a new post in a language

    :param args:
    :param permission_level:
    :param connection:
    :param post_type:
    :param lang_id:
    :param kwargs:
    :return:
    """
    data = prepare_data_new_post(connection=connection, post_type=post_type, lang_id=lang_id)
    data["permission_level"] = permission_level
    return json.dumps(data), 200


def prepare_data_new_post(connection: psycopg.Connection, post_type: str, lang_id: str):
    original_post = request.args.get('original');
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    media = []
    post_type_name = ""
    try:
        media = get_media(connection=connection)
        with connection.cursor() as cur:
            cur.execute("SELECT display_name FROM sloth_post_types WHERE uuid = %s",
                        (post_type,))
            post_type_name = cur.fetchone()[0]
            cur.execute("SELECT unnest(enum_range(NULL::sloth_post_status))")
            temp_post_statuses = cur.fetchall()
            cur.execute("""SELECT uuid, display_name, taxonomy_type, slug FROM sloth_taxonomy
                                                WHERE post_type = %s AND lang = %s""",
                        (post_type, lang_id))
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
                cur.execute("""SELECT content, section_type, position
                            FROM sloth_post_sections
                            WHERE post = %s
                            ORDER BY position;""",
                            (original_post,))
                sections = [{
                    "content": "",
                    "original": section[0],
                    "type": section[1],
                    "position": section[2],
                } for section in cur.fetchall()]
            else:
                translatable_languages = languages
                translations = []
            cur.execute("""SELECT uuid, slug, display_name FROM sloth_post_formats WHERE post_type = %s""",
                        (post_type,))
            post_formats = [{
                "uuid": pf[0],
                "slug": pf[1],
                "display_name": pf[2]
            } for pf in cur.fetchall()]

            cur.execute("""SELECT uuid FROM sloth_post_formats WHERE post_type = %s AND deletable = %s """,
                        (post_type, False))
            default_format = cur.fetchone()[0]

            cur.execute("""SELECT uuid, name, version, location 
                        FROM sloth_libraries;""")
            libs = [{
                "uuid": lib[0],
                "name": lib[1],
                "version": lib[2],
                "location": lib[3]
            } for lib in cur.fetchall()]
            post_libs = []
    except Exception as e:
        connection.close()
        print(e)
        abort(500)

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
        "original_lang_entry_uuid": original_post,
        "post_format_uuid": default_format,
        "libraries": post_libs,
        "categories": categories,
        "tags": tags,
        "sections": sections,
    }

    return {
        "title": f"Add new {post_type_name}" if data["new"] else f"Edit {post_type_name}",
        "post_types": post_types_result,
        "post_type_name": post_type_name,
        "data": data,
        "media_data": json.dumps([media[key] for key in media.keys()]),
        "post_statuses": [item for sublist in temp_post_statuses for item in sublist],
        "default_lang": default_lang,
        "languages": translatable_languages,
        "translations": translations,
        "current_lang_id": data["lang"],
        "post_formats": post_formats,
        "libs": libs,
        "hook_list": HooksList.list()
    }


@post.route("/post/<type_id>/taxonomy")
@authorize_web(0)
@db_connection
def show_post_taxonomy_main_lang(*args, permission_level: int, connection: psycopg.Connection, type_id: str, **kwargs):
    """
    Renders a list of taxonomies for default language

    :param args:
    :param permission_level:
    :param connection:
    :param type_id:
    :param kwargs:
    :return:
    """
    return show_taxonomy(
        permission_level=permission_level,
        connection=connection,
        type_id=type_id,
        lang_id=get_default_language(connection=connection)["uuid"]
    )


@post.route("/post/<type_id>/taxonomy/<lang_id>")
@authorize_web(0)
@db_connection
def show_post_taxonomy(*args, permission_level: int, connection: psycopg.Connection, type_id: str, lang_id: str,
                       **kwargs):
    """
    Renders a list of taxonomies for a language

    :param args:
    :param permission_level:
    :param connection:
    :param type_id:
    :param lang_id:
    :param kwargs:
    :return:
    """
    return show_taxonomy(
        permission_level=permission_level,
        connection=connection,
        type_id=type_id,
        lang_id=lang_id
    )


def show_taxonomy(*args, permission_level: int, connection: psycopg.Connection, type_id: str, lang_id: str, **kwargs):
    """
    Renders a list of taxonomies

    :param args:
    :param permission_level:
    :param connection:
    :param type_id:
    :param lang_id:
    :param kwargs:
    :return:
    """
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    taxonomy = {}
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT unnest(enum_range(NULL::sloth_taxonomy_type))")
            taxonomy_types = [item for sublist in cur.fetchall() for item in sublist]
            for taxonomy_type in taxonomy_types:
                cur.execute("""SELECT uuid, display_name 
                    FROM sloth_taxonomy WHERE post_type = %s AND taxonomy_type = %s AND lang = %s""",
                            (type_id, taxonomy_type, lang_id))
                taxonomy[taxonomy_type] = cur.fetchall()
    except Exception as e:
        print("db error C")
        abort(500)

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
@db_connection
def show_formats(*args, permission_level: int, connection: psycopg.Connection, type_id: str, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    lang_id = get_default_language(connection=connection)["uuid"]

    try:
        with connection.cursor() as cur:
            cur.execute(
                """SELECT uuid, slug, display_name, deletable
                     FROM sloth_post_formats
                     WHERE post_type = %s""",
                (type_id,))
            post_formats = [{
                "uuid": pt[0],
                "slug": pt[1],
                "display_name": pt[2],
                "deletable": pt[3]
            } for pt in cur.fetchall()]
    except Exception as e:
        print("db error C")
        connection.close()
        abort(500)

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
@db_connection
def save_post_format(*args, connection: psycopg.Connection, **kwargs):
    filled = json.loads(request.data)
    slug_changed = False
    try:
        with connection.cursor() as cur:
            if filled['uuid'] != 'new':
                cur.execute("""SELECT slug FROM sloth_post_formats WHERE uuid = %s;""",
                            (filled["uuid"],))
                old_slug = cur.fetchone()[0]
                if filled['slug'] != old_slug:
                    slug_changed = True

            if slug_changed or filled['uuid'] == 'new':
                cur.execute(
                    """SELECT count(slug) FROM sloth_post_formats 
                        WHERE slug LIKE %s OR slug LIKE %s AND post_type=%s;""",
                    (f"{filled['slug']}-%", f"{filled['slug']}%", filled["post_type_uuid"]))
                similar = cur.fetchone()[0]
                if int(similar) > 0:
                    filled['slug'] = f"{filled['slug']}-{str(int(similar) + 1)}"

            if filled['uuid'] == 'new':
                cur.execute(
                    """INSERT INTO sloth_post_formats (uuid, slug, display_name, post_type, deletable) 
                        VALUES (%s, %s, %s, %s, %s) RETURNING uuid, slug, display_name, deletable;""",
                    (str(uuid.uuid4()), filled['slug'], filled["display_name"], filled["post_type_uuid"], True))
            else:
                cur.execute(
                    """UPDATE sloth_post_formats SET slug = %s, display_name = %s 
                        WHERE uuid = %s RETURNING uuid, slug, display_name, deletable;""",
                    (filled['slug'], filled["display_name"], filled["uuid"]))
            raw_result = cur.fetchone()
            connection.commit()
    except Exception as e:
        print("db error C")
        connection.close()
        abort(500)

    connection.close()

    return json.dumps({
        "uuid": raw_result[0],
        "display_name": raw_result[2],
        "slug": raw_result[1],
        "deletable": raw_result[3]
    }), 200


@post.route("/api/post/formats", methods=["DELETE"])
@authorize_web(0)
@db_connection
def delete_post_format(*args, permission_level, connection: psycopg.Connection, **kwargs):
    filled = json.loads(request.data)
    try:
        with connection.close() as cur:
            cur.execute(
                """DELETE FROM sloth_post_formats
                     WHERE uuid = %s AND deletable = %s""",
                (filled["uuid"], True))
            connection.commit()
            cur.execute(
                """SELECT uuid FROM sloth_post_formats
                     WHERE uuid = %s""",
                (filled["uuid"],))
        if len(cur.fetchall()) > 0:
            connection.close()
            return escape(json.dumps({
                "uuid": filled["uuid"],
                "deleted": False
            })), 406
    except Exception as e:
        print("db error C")
        connection.close()
        abort(500)

    connection.close()

    return escape(json.dumps({
        "uuid": filled["uuid"],
        "deleted": True
    })), 204


@post.route("/post/<type_id>/taxonomy/<taxonomy_type>/<taxonomy_id>", methods=["GET"])
@authorize_web(0)
@db_connection
def show_post_taxonomy_item(*args, permission_level: int, connection: psycopg.Connection, type_id: str,
                            taxonomy_id: str, taxonomy_type: str, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    try:
        with connection.cursor() as cur:
            cur.execute("""SELECT slug, display_name 
                FROM sloth_taxonomy WHERE post_type = %s AND uuid = %s""",
                        (type_id, taxonomy_id))
            temp_taxonomy = cur.fetchone()
    except Exception as e:
        print("db error C")
        connection.close()
        abort(500)

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
def save_post_taxonomy_item(*args, connection: psycopg.Connection, type_id: str, taxonomy_id: str, taxonomy_type: str,
                            **kwargs):
    filled = request.form

    if filled["slug"] or filled["display_name"]:
        redirect(f"/post/{type_id}/taxonomy/{taxonomy_id}?error=missing_data")
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT display_name FROM sloth_taxonomy WHERE uuid = %s;",
                        (taxonomy_id,))
            res = cur.fetchall()
            if len(res) == 0:
                cur.execute(
                    """INSERT INTO sloth_taxonomy (uuid, slug, display_name, post_type, taxonomy_type, lang) 
                        VALUES (%s, %s, %s, %s, %s, %s);""",
                    (taxonomy_id, filled["slug"], filled["display_name"], type_id, taxonomy_type, filled["language"]))
            else:
                cur.execute("""UPDATE sloth_taxonomy SET slug = %s, display_name = %s WHERE uuid = %s;""",
                            (filled["slug"], filled["display_name"], taxonomy_id))
            connection.commit()
    except Exception as e:
        connection.close()
        return redirect(f"/post/{type_id}/taxonomy/{taxonomy_type}/{taxonomy_id}?error=db")

    connection.close()
    return redirect(f"/post/{type_id}/taxonomy/{taxonomy_type}/{taxonomy_id}")


@post.route("/post/<type_id>/taxonomy/<taxonomy_type>/new")
@authorize_web(0)
@db_connection
def create_taxonomy_item(*args, permission_level: int, connection: psycopg.Connection, type_id: str, taxonomy_type: str,
                         **kwargs):
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
def get_media_data(*args, connection: psycopg.Connection, lang_id: str, **kwargs):
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT settings_value FROM sloth_settings WHERE settings_name = 'site_url'")
            site_url = cur.fetchone()
            site_url = site_url[0] if len(site_url) > 0 else ""
            cur.execute("SELECT uuid, file_path FROM sloth_media")
            raw_media = cur.fetchall()
            media = {medium[0]: {
                "uuid": medium[0],
                "filePath": f"{site_url}/{medium[1]}"
            } for medium in raw_media}
            cur.execute(
                """SELECT media, alt FROM sloth_media_alts
                               WHERE lang = %s;""",
                (lang_id,))
            alts = cur.fetchall()
            for alt in alts:
                if media[alt[0]] is not None:
                    media[alt[0]]["alt"] = alt[1]
    except Exception as e:
        print("db error")
        connection.close()
        abort(500)

    connection.close()

    return json.dumps({"media": list(media.values())})


@post.route("/api/post/upload-file", methods=['POST'])
@authorize_rest(0)
@db_connection
def upload_image(*args, file_name: str, connection: psycopg.Connection, **kwargs):
    """
    API endpoint for uploading a file
    TODO check file_name type

    :param args:
    :param file_name:
    :param connection:
    :param kwargs:
    :return:
    """
    ext = file_name[file_name.rfind("."):]
    if not ext.lower() in (".png", ".jpg", ".jpeg", ".svg", ".bmp", ".tiff"):
        abort(500)
    with open(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", file_name), 'wb') as f:
        f.write(request.data)

    try:
        with connection.cursor() as cur:
            cur.execute("INSERT INTO sloth_media VALUES (%s, %s, %s) RETURNING uuid, file_path",
                        (str(uuid.uuid4()), os.path.join("sloth-content", file_name), ""))
            file = cur.fetchone()
    except Exception as e:
        print(traceback.format_exc())
        connection.close()
        abort(500)

    connection.close()

    return json.dumps({"media": file}), 201


@post.route("/api/post", methods=['POST'])
@authorize_rest(0)
@db_connection
def save_post(*args, connection: psycopg.Connection, **kwargs):
    """
    API endpoint to save a post

    :param args:
    :param connection:
    :param kwargs:
    :return:
    """
    result = {}
    filled = json.loads(request.data)
    filled["thumbnail"] = filled["thumbnail"] if len(filled["thumbnail"]) > 0 else None
    try:
        with connection.cursor() as cur:
            if "lang" not in filled:
                cur.execute("SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language';")
                lang = cur.fetchone()[0]
            else:
                lang = filled["lang"]
                matched_tags = process_taxonomy(connection=connection, post_tags=filled["tags"], post_type_uuid=filled["post_type_uuid"], lang=lang)
                # get user
                author = request.headers.get('authorization').split(":")[1]

                publish_date = generate_publish_date(status=filled["post_status"], date=filled["publish_date"])

                # save post
                if filled["new"] and str(filled["new"]).lower() != 'none':
                    unique_post = False
                    while filled["new"] and not unique_post:
                        cur.execute("SELECT count(uuid) FROM sloth_posts WHERE uuid = %s",
                                    (filled["uuid"],))
                        if cur.fetchone()[0] != 0:
                            filled["uuid"] = str(uuid.uuid4())
                        else:
                            unique_post = True

                    cur.execute(
                        "SELECT count(slug) FROM sloth_posts WHERE slug LIKE %s OR slug LIKE %s AND post_type=%s;",
                        (f"{filled['slug']}-%", f"{filled['slug']}%", filled["post_type_uuid"]))
                    similar = cur.fetchone()[0]
                    if int(similar) > 0:
                        filled['slug'] = f"{filled['slug']}-{str(int(similar) + 1)}"

                    cur.execute("""INSERT INTO sloth_posts (uuid, slug, post_type, author, 
                        title, css, js, thumbnail, publish_date, update_date, post_status, lang, password,
                        original_lang_entry_uuid, post_format, meta_description, twitter_description, pinned) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                (filled["uuid"], filled["slug"], filled["post_type_uuid"], author, filled["title"],
                                 filled["css"], filled["js"], filled["thumbnail"], publish_date, str(time() * 1000),
                                 filled["post_status"], lang, filled["password"] if "password" in filled else None,
                                 filled["original_lang_entry_uuid"] if "original_lang_entry_uuid" in filled else "", filled["post_format"],
                                 filled["meta_description"], filled["twitter_description"], filled["pinned"]))
                    connection.commit()
                    taxonomy_to_clean = sort_out_post_taxonomies(connection=connection, article=filled,
                                                                 tags=matched_tags)
                    result["uuid"] = filled["uuid"]
                else:
                    # when editting this don't forget that last item needs to be uuid
                    cur.execute("""UPDATE sloth_posts SET slug = %s, title = %s, css = %s, js = %s,
                         thumbnail = %s, publish_date = %s, update_date = %s, post_status = %s, import_approved = %s,
                         password = %s, post_format = %s, meta_description = %s, twitter_description = %s,
                          pinned = %s WHERE uuid = %s;""",
                                (filled["slug"], filled["title"], filled["css"], filled["js"],
                                 filled["thumbnail"] if filled["thumbnail"] != "None" else None,
                                 filled["publish_date"] if filled["publish_date"] is not None else publish_date,
                                 str(time() * 1000), filled["post_status"], filled["approved"],
                                 filled["password"] if "password" in filled else None, filled["post_format"],
                                 filled["meta_description"], filled["twitter_description"], filled["pinned"],
                                 filled["uuid"]))
                    connection.commit()
                    taxonomy_to_clean = sort_out_post_taxonomies(connection=connection, article=filled,
                                                                 tags=matched_tags)

                # save libraries
                cur.execute("""DELETE FROM sloth_post_libraries WHERE post = %s;""",
                            (filled["uuid"],))
                for lib in filled["libs"]:
                    cur.execute(
                        """INSERT INTO sloth_post_libraries (uuid, post, library, hook_name)  VALUES (%s, %s, %s, %s)""",
                        (str(uuid.uuid4()), filled["uuid"], lib["libId"], lib["hook"]))
                connection.commit()

                cur.execute("""DELETE from sloth_post_sections WHERE post = %s;""",
                            (filled["uuid"],))
                cur.execute(build_post_query(uuid=True), (filled["uuid"],))
                saved_post = normalize_post_from_query(cur.fetchone())
                sections = process_sections(connection, filled["sections"], filled["uuid"])
                saved_post.update({
                    "meta_description": prepare_description(char_limit=161, description=saved_post["meta_description"], section=sections[0]),
                    "twitter_description": prepare_description(char_limit=161, description=saved_post["twitter_description"], section=sections[0]),
                    "sections": sections,
                })
                cur.execute(
                    """SELECT sl.location, spl.hook_name
                    FROM sloth_post_libraries AS spl
                    INNER JOIN sloth_libraries sl on sl.uuid = spl.library
                    WHERE spl.post = %s;""",
                    (filled["uuid"],))
                saved_post["libraries"] = [{
                    "location": lib[0],
                    "hook_name": lib[1]
                } for lib in cur.fetchall()]
                saved_post["related_posts"] = get_related_posts(post=saved_post, connection=connection)
                # get post
                if filled["post_status"] == 'published':
                    gen = PostGenerator(connection=connection)
                    gen.run(post=saved_post, regenerate_taxonomies=taxonomy_to_clean)
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
                    cur.execute("""SELECT slug, uuid FROM sloth_post_types WHERE uuid = %s;""",
                                (saved_post["post_type"],))
                    post_type = cur.fetchone()
                    cur.execute("""SELECT uuid, short_name, long_name FROM sloth_language_settings WHERE uuid = %s;""",
                                (saved_post["lang"],))
                    language_raw = cur.fetchone()
                    # get post slug
                    gen = PostGenerator()
                    gen.delete_post_files(
                        post_type_slug=post_type[0],
                        post_slug=saved_post["slug"],
                        language={
                            "uuid": language_raw[0],
                            "short_name": language_raw[1],
                            "long_name": language_raw[2]
                        }
                    )
                    gen.run(clean_protected=True, post=saved_post)
    except Exception:
        print(traceback.format_exc())
        return json.dumps({"error": "Error saving post"}), 500

    result["saved"] = True
    result["postType"] = saved_post["post_type"]
    return json.dumps(result)


def process_sections(connection: psycopg.Connection, sections: List, post_uuid: str) -> List:
    with connection.cursor() as cur:
        for section in sections:
            cur.execute("""INSERT INTO sloth_post_sections VALUES (%s, %s, %s, %s, %s)""",
                        (str(uuid.uuid4()), post_uuid, section["content"], section["type"],
                         section["position"]))
        connection.commit()

        cur.execute(
            """SELECT content, section_type, position
            FROM sloth_post_sections
            WHERE post = %s
            ORDER BY position;""",
            (post_uuid,))
        processed_sections = [{
            "content": section[0],
            "type": section[1],
            "position": section[2]
        } for section in cur.fetchall()]
        return processed_sections


def generate_publish_date(status: str, date: str | None) -> str | None:
    """

    :param status:
    :param date:
    :return:
    """
    if (status == 'published' and date is None) or (
            status == 'protected' and date is None):
        return str(time() * 1000)
    if status == 'scheduled':
        return date

    return None


def process_taxonomy(connection: psycopg.Connection, post_tags: List, post_type_uuid: str, lang: str) -> List:
    """

    :param connection:
    :param post_tags:
    :param post_type_uuid:
    :param lang:
    :return:
    """
    with connection.cursor() as cur:
        cur.execute("""SELECT uuid, slug, display_name, post_type, taxonomy_type 
                                    FROM sloth_taxonomy 
                                    WHERE post_type = %s AND taxonomy_type = 'tag' AND lang = %s;""",
                    (post_type_uuid, lang))
        existing_tags = cur.fetchall()

        existing_tags_slugs = [slug[1] for slug in existing_tags]

        matched_tags = []
        new_tags = []
        for tag in post_tags:
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
            cur.execute("""INSERT INTO sloth_taxonomy (uuid, slug, display_name, post_type, taxonomy_type, lang) 
                                            VALUES (%s, %s, %s, %s, 'tag', %s);""",
                        (new_tag["uuid"], new_tag["slug"], new_tag["displayName"], post_type_uuid, lang))
            matched_tags.append(new_tag)

        connection.commit()
        return matched_tags


def sort_out_post_taxonomies(*args, connection: psycopg.Connection, article: Dict, tags: List, **kwargs) -> List:
    """
    Sorts out post taxonomies to be deleted

    :param args:
    :param connection:
    :param article:
    :param tags:
    :param kwargs:
    :return:
    """
    try:
        with connection.cursor() as cur:
            categories = article["categories"]
            cur.execute("""SELECT uuid, taxonomy FROM sloth_post_taxonomies WHERE post = %s;""",
                        (article["uuid"],))
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
                cur.execute("""DELETE FROM sloth_post_taxonomies WHERE uuid = %s""",
                            (taxonomy["uuid"],))
                taxonomies.remove(taxonomy)
            connection.commit()

            for category in categories:
                cur.execute("""INSERT INTO sloth_post_taxonomies (uuid, post, taxonomy) VALUES (%s, %s, %s)""",
                            (str(uuid.uuid4()), article["uuid"], category))
            for tag in tags:
                cur.execute("""INSERT INTO sloth_post_taxonomies (uuid, post, taxonomy) VALUES (%s, %s, %s)""",
                            (str(uuid.uuid4()), article["uuid"], tag["uuid"]))
            connection.commit()
    except Exception:
        return []

    return for_deletion


@post.route("/api/post/delete", methods=['POST', 'DELETE'])
@authorize_rest(0)
@db_connection
def delete_post(*args, connection: psycopg.Connection, **kwargs):
    """
    API endpoint to delete a post

    :param args:
    :param connection:
    :param kwargs:
    :return:
    """

    filled = json.loads(request.data)

    try:
        with connection.cursor() as cur:
            cur.execute("""SELECT A.post_type, A.slug, spt.slug, A.lang 
                FROM sloth_posts as A INNER JOIN sloth_post_types spt on A.post_type = spt.uuid WHERE A.uuid = %s""",
                        (filled["post"],))
            res = cur.fetchone()
            cur.execute("""SELECT A.uuid 
                        FROM sloth_posts as A WHERE A.original_lang_entry_uuid = %s ORDER BY publish_date ASC""",
                        (filled["post"],))
            oldest_alternative = cur.fetchone()
            cur.execute("""UPDATE sloth_posts SET original_lang_entry_uuid = '' WHERE uuid = %s;""",
                        oldest_alternative)
            cur.execute("""UPDATE sloth_posts SET original_lang_entry_uuid = %s WHERE original_lang_entry_uuid = %s;""",
                        (oldest_alternative[0], filled["post"]))
            cur.execute("""DELETE FROM sloth_post_taxonomies WHERE post = %s;""",
                        (filled["post"],))
            cur.execute("""DELETE FROM sloth_post_sections WHERE post = %s;""",
                        (filled["post"],))
            cur.execute("DELETE FROM sloth_posts WHERE uuid = %s",
                        (filled["post"],))
            connection.commit()
            cur.execute("SELECT COUNT(uuid) FROM sloth_posts")
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
@db_connection
def delete_taxonomy(*args, connection: psycopg.Connection, taxonomy_id: str, **kwargs):
    """
    API end point to delete taxonomy
    TODO check this when designing API

    :param args:
    :param connection:
    :param taxonomy_id:
    :param kwargs:
    :return:
    """

    try:
        with connection.cursor() as cur:
            cur.execute("DELETE FROM sloth_taxonomy WHERE uuid = %s;",
                        (taxonomy_id,))
            connection.commit()
    except Exception as e:
        connection.close()
        return json.dumps({"error": "db"})
    connection.close()
    return json.dumps({"deleted": True})


@post.route("/api/post/regenerate-all", methods=["POST", "PUT"])
@authorize_rest(0)
@db_connection
def regenerate_all(*args, connection: psycopg.Connection, **kwargs):
    """
    API endpoint to trigger regenerating all blog content

    :param args:
    :param connection:
    :param kwargs:
    :return:
    """

    gen = PostGenerator(connection=connection)
    gen.run()

    return json.dumps({"generating": True})


@post.route("/api/post/refresh-assets", methods=["POST", "PUT"])
@authorize_rest(0)
@db_connection
def refresh_assets(*args, connection: psycopg.Connection, **kwargs):
    """
    API endpoint to trigger regenerating all blog content

    :param args:
    :param connection:
    :param kwargs:
    :return:
    """

    gen = PostGenerator(connection=connection)
    gen.refresh_assets()

    return json.dumps({"refreshed": True})


@post.route("/api/post/secret", methods=["POST"])
@db_connection
def get_protected_post(*args, connection: psycopg.Connection, **kwargs):
    """
    TODO implement accessing password protected posts properly after Rust Toes

    :param args:
    :param connection:
    :param kwargs:
    :return:
    """
    filled = json.loads(request.data)

    try:
        with connection.cursor() as cur:
            cur.execute("""SELECT uuid 
                FROM sloth_posts WHERE password = %s AND slug = %s;""",
                        (filled["password"], filled["slug"]))
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
def is_generating(*args, **kwargs):
    """
    API endpoint to check whether Sloth is generating the files

    :param args:
    :param kwargs:
    :return:
    """
    return json.dumps({
        "generating": Path(os.path.join(os.getcwd(), 'generating.lock')).is_file()
    })
