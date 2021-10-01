from flask import flash, render_template, abort, make_response, request
import json
from psycopg2 import sql
import uuid
from app.authorization.authorize import authorize_web, authorize_rest
import datetime

from app.utilities.db_connection import db_connection_legacy
from app.utilities import get_languages, get_default_language
from app.post.post_types import PostTypes

from app.settings.themes.menu import menu


@menu.route("/settings/themes/menu")
@authorize_web(0)
@db_connection_legacy
def show_menus(*args, permission_level, connection, **kwargs):
    cur = connection.cursor()
    main_lang = ""
    try:
        cur.execute(
            sql.SQL("""SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language';""")
        )
        main_lang = cur.fetchone()[0]
    except Exception as e:
        print(e)
        abort(500)

    return return_menu_language(permission_level=permission_level, connection=connection, lang_id=main_lang)


@menu.route("/settings/themes/menu/<lang_id>")
@authorize_web(0)
@db_connection_legacy
def show_lang_menus(*args, permission_level, connection, lang_id, **kwargs):
    return return_menu_language(permission_level=permission_level, connection=connection, lang_id=lang_id)


def return_menu_language(*args, permission_level, connection, lang_id, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    cur = connection.cursor()
    temp_result = []
    temp_menu_types = []
    try:
        cur.execute(
            sql.SQL("""SELECT uuid, name FROM sloth_menus WHERE lang = %s;"""),
            [lang_id]
        )
        temp_result = cur.fetchall()
        cur.execute(
            sql.SQL("""SELECT unnest(enum_range(NULL::sloth_menu_item_types))""")
        )
        temp_menu_types = cur.fetchall()
    except Exception as e:
        print(e)
        abort(500)

    result = [{
        "uuid": item[0],
        "name": item[1]
    } for item in temp_result]
    cur.close()
    current_lang, languages = get_languages(connection=connection, lang_id=lang_id)
    default_lang = get_default_language(connection=connection)

    return render_template(
        "menu.html",
        permission_level=permission_level,
        post_types=post_types_result,
        menus=result,
        item_types=[item for sublist in temp_menu_types for item in sublist],
        languages=languages,
        default_lang=default_lang,
        current_lang=current_lang
    )


@menu.route("/api/settings/themes/menu/<menu>")
@authorize_rest(0)
@db_connection_legacy
def get_menu(*args, connection, menu, **kwargs):
    cur = connection.cursor()
    temp_result = []
    try:
        cur.execute(
            sql.SQL("""SELECT uuid, title, type, url, position FROM sloth_menu_items WHERE menu = %s;"""),
            [menu]
        )
        temp_result = cur.fetchall()
    except Exception as e:
        print(e)
        abort(500)

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
@db_connection_legacy
def save_menu(*args, connection, **kwargs):
    if connection is None:
        abort(500)

    filled = json.loads(request.data)

    cur = connection.cursor()
    result = []
    try:
        if filled["uuid"].startswith("new-"):
            cur.execute(
                sql.SQL("""INSERT INTO sloth_menus VALUES (%s, %s)
                            RETURNING name, uuid;"""),
                [str(uuid.uuid4()), filled["name"]]
            )
        else:
            cur.execute(
                sql.SQL("""UPDATE sloth_menus SET name = %s WHERE uuid = %s
                RETURNING name, uuid;"""),
                [filled["name"], filled["uuid"]]
            )
        connection.commit()
        temp_result = cur.fetchone()
        result = {
            "name": temp_result[0],
            "uuid": temp_result[1]
        }
        for item in filled["items"]:
            if item["uuid"].startswith("new-"):
                cur.execute(
                    sql.SQL("""INSERT INTO sloth_menu_items VALUES (%s, %s, %s, %s, %s, %s);"""),
                    [str(uuid.uuid4()), result["uuid"], item["title"], item["type"], item["uri"], item["position"]]
                )
            else:
                cur.execute(
                    sql.SQL("""UPDATE sloth_menu_items SET title = %s, type = %s, url = %s, position = %s 
                    WHERE uuid = %s;"""),
                    [item["title"], item["type"], item["uri"], item["position"], item["uuid"]]
                )
        connection.commit()
    except Exception as e:
        print(e)
        abort(500)

    cur.close()
    connection.close()

    return json.dumps(result)


@menu.route("/api/settings/themes/menu/delete", methods=["DELETE"])
@authorize_rest(0)
@db_connection_legacy
def delete_menu(*args, connection, **kwargs):
    filled = json.loads(request.data)
    if not filled["menu"] or len(filled["menu"]) == 0:
        response = make_response(json.dumps({"menuDeleted": filled["menu"]}))
        response.headers['Content-Type'] = 'application/json'
        return response, 400

    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL("""DELETE FROM sloth_menu_items WHERE menu = %s"""),
            [filled["menu"]]
        )
        cur.execute(
            sql.SQL("""DELETE FROM sloth_menus WHERE uuid = %s"""),
            [filled["menu"]]
        )
        connection.commit()
    except Exception as e:
        print(e)
        abort(500)
    cur.close()
    connection.close()
    response = make_response(json.dumps({"menuDeleted": filled["menu"]}))
    response.headers['Content-Type'] = 'application/json'
    return response, 204
