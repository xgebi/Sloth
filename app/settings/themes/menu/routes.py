from flask import flash, render_template, abort, make_response, request
import json
from psycopg2 import sql
import uuid
from app.authorization.authorize import authorize_web, authorize_rest
import datetime

from app.utilities.db_connection import db_connection
from app.post.post_types import PostTypes

from app.settings.themes.menu import menu


@menu.route("/settings/themes/menu")
@authorize_web(0)
@db_connection
def show_menus(*args, permission_level, connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    cur = connection.cursor()
    temp_result = []
    temp_menu_types = []
    try:
        cur.execute(
            sql.SQL("""SELECT uuid, name FROM sloth_menus""")
        )
        temp_result = cur.fetchall()
        cur.execute(
            sql.SQL("SELECT unnest(enum_range(NULL::sloth_menu_item_types))")
        )
        temp_menu_types = cur.fetchall()
    except Exception as e:
        print(e)
        abort(500)

    result = []
    for item in temp_result:
        result.append({
            "uuid": item[0],
            "name": item[1]
        })

    return render_template(
        "menu.html",
        permission_level=permission_level,
        post_types=post_types_result,
        menus=result,
        item_types=[item for sublist in temp_menu_types for item in sublist]
    )


@menu.route("/settings/themes/menu/<menu>")
@authorize_rest(0)
@db_connection
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

    response = make_response(json.dumps(result))
    response.headers['Content-Type'] = 'application/json'

    return response


@menu.route("/settings/themes/menu/save", methods=["POST", "PUT"])
@authorize_rest(0)
@db_connection
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


@menu.route("/settings/themes/menu/delete", methods=["DELETE"])
@authorize_web(0)
@db_connection
def delete_menu(*args, permission_level, connection, **kwargs):

    return json.dumps({})
