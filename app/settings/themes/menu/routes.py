from flask import flash, render_template, abort, make_response
import json
from psycopg2 import sql
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
    try:
        cur.execute(
            sql.SQL("""SELECT uuid, name FROM sloth_menus""")
        )
        temp_result = cur.fetchall()
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
        menus=result
    )


@menu.route("/settings/themes/menu/<menu>")
@authorize_rest(0)
@db_connection
def get_menu(*args, connection, menu, **kwargs):
    cur = connection.cursor()
    temp_result = []
    try:
        cur.execute(
            sql.SQL("""SELECT uuid, title, type, url FROM sloth_menu_items WHERE menu = %s;"""),
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
            "url": item[3]
        })

    response = make_response(json.dumps(result))
    response.headers['Content-Type'] = 'application/json'

    return response


@menu.route("/settings/themes/menu/save", methods=["POST", "PUT"])
@authorize_web(0)
@db_connection
def save_menu(*args, permission_level, connection, **kwargs):
    if connection is None:
        abort(500)

    return json.dumps({})


@menu.route("/settings/themes/menu/delete", methods=["DELETE"])
@authorize_web(0)
@db_connection
def delete_menu(*args, permission_level, connection, **kwargs):

    return json.dumps({})
