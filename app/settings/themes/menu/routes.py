import psycopg
from flask import escape, abort, make_response, request
import json
import uuid
import os
from app.toes.hooks import Hooks
from app.authorization.authorize import authorize_web, authorize_rest
from app.toes.toes import render_toe_from_path

from app.utilities.db_connection import db_connection
from app.utilities import get_languages, get_default_language
from app.post.post_types import PostTypes

from app.settings.themes.menu import menu


@menu.route("/settings/themes/menu")
@authorize_web(0)
@db_connection
def show_menus(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
    try:
        with connection.cursor() as cur:
            cur.execute("""SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language';""")
            main_lang = cur.fetchone()[0]
    except Exception as e:
        print(e)
        connection.close()
        abort(500)

    return return_menu_language(permission_level=permission_level, connection=connection, lang_id=main_lang)


@menu.route("/settings/themes/menu/<lang_id>")
@authorize_web(0)
@db_connection
def show_lang_menus(*args, permission_level: int, connection: psycopg.Connection, lang_id: str, **kwargs):
    return return_menu_language(permission_level=permission_level, connection=connection, lang_id=lang_id)


def return_menu_language(*args, permission_level: int, connection: psycopg.Connection, lang_id: str, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    temp_result = []
    temp_menu_types = []
    try:
        with connection.cursor() as cur:
            cur.execute("""SELECT uuid, name FROM sloth_menus WHERE lang = %s;""",
                        (lang_id, ))
            temp_result = cur.fetchall()
            cur.execute("""SELECT unnest(enum_range(NULL::sloth_menu_item_types))""")
            temp_menu_types = cur.fetchall()
    except Exception as e:
        print(e)
        connection.close()
        abort(500)

    result = [{
        "uuid": item[0],
        "name": item[1]
    } for item in temp_result]
    current_lang, languages = get_languages(connection=connection, lang_id=lang_id)
    default_lang = get_default_language(connection=connection)

    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="menu.toe.html",
        data={
            "title": "List of media",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "menus": result,
            "item_types": [item for sublist in temp_menu_types for item in sublist],
            "default_lang": default_lang,
            "languages": languages,
            "current_lang": current_lang,
        },
        hooks=Hooks()
    )


@menu.route("/api/settings/themes/menu/<menu_str>")
@authorize_rest(0)
@db_connection
def get_menu(*args, connection: psycopg.Connection, menu_str: str, **kwargs):
    try:
        with connection.cursor() as cur:
            cur.execute("""SELECT uuid, title, type, url, position FROM sloth_menu_items WHERE menu = %s;""",
                        (menu_str, ))
            temp_result = cur.fetchall()
    except Exception as e:
        print(e)
        connection.close()
        abort(500)
    connection.close()

    result = []
    for item in temp_result:
        result.append({
            "uuid": item[0],
            "title": item[1],
            "type": item[2],
            "url": item[3],
            "position": item[4]
        })

    return json.dumps(result), 200, {'Content-Type': 'application/json'}


@menu.route("/api/settings/themes/menu/save", methods=["POST", "PUT"])
@authorize_rest(0)
@db_connection
def save_menu(*args, connection: psycopg.Connection, **kwargs):
    filled = json.loads(request.data)

    try:
        with connection.cursor() as cur:
            if filled["uuid"].startswith("new-"):
                cur.execute("""INSERT INTO sloth_menus (uuid, name, lang) VALUES (%s, %s, %s)
                                RETURNING name, uuid;""",
                            (str(uuid.uuid4()), filled["name"], filled['language']))
            else:
                cur.execute("""UPDATE sloth_menus SET name = %s WHERE uuid = %s
                    RETURNING name, uuid;""",
                            (filled["name"], filled["uuid"]))
            connection.commit()
            temp_result = cur.fetchone()
            result = {
                "name": temp_result[0],
                "uuid": temp_result[1]
            }
            for item in filled["items"]:
                if item["uuid"].startswith("new-"):
                    cur.execute("""INSERT INTO sloth_menu_items VALUES (%s, %s, %s, %s, %s, %s);""",
                                (str(uuid.uuid4()), result["uuid"], item["title"], item["type"], item["uri"], item["position"]))
                else:
                    cur.execute("""UPDATE sloth_menu_items SET title = %s, type = %s, url = %s, position = %s 
                        WHERE uuid = %s;""",
                                (item["title"], item["type"], item["uri"], item["position"], item["uuid"]))
            connection.commit()
    except Exception as e:
        print(e)
        connection.close()
        abort(500)

    connection.close()

    return json.dumps(result)


@menu.route("/api/settings/themes/menu/delete", methods=["DELETE"])
@authorize_rest(0)
@db_connection
def delete_menu(*args, connection: psycopg.Connection, **kwargs):
    filled = json.loads(request.data)
    if not filled["menu"] or len(filled["menu"]) == 0:
        response = make_response(escape(json.dumps({"menuDeleted": filled["menu"]})))
        response.headers['Content-Type'] = 'application/json'
        return response, 400

    try:
        with connection.cursor() as cur:
            cur.execute("""DELETE FROM sloth_menu_items WHERE menu = %s""",
                        (filled["menu"], ))
            cur.execute("""DELETE FROM sloth_menus WHERE uuid = %s""",
                        (filled["menu"], ))
            connection.commit()
    except Exception as e:
        print(e)
        connection.close()
        abort(500)

    connection.close()
    response = make_response(escape(json.dumps({"menuDeleted": filled["menu"]})))
    response.headers['Content-Type'] = 'application/json'
    return response, 204
