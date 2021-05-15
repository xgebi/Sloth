from flask import abort, request, redirect, current_app, make_response
from app.authorization.authorize import authorize_web
from app.utilities.db_connection import db_connection
from app.toes.hooks import Hooks
from app.toes.toes import render_toe_from_path
from app.post.post_types import PostTypes
from app.utilities import get_default_language
from psycopg2 import sql
import os
import traceback
import json
from uuid import uuid4

from app.libraries import libraries


# display libraries
@libraries.route("/libraries")
@authorize_web(0)
@db_connection
def show_libraries(*args, permission_level, connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    default_language = get_default_language(connection=connection)

    try:
        cur = connection.cursor()

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

        cur.close()
        connection.close()
    except Exception as e:
        print(traceback.format_exc())
        abort(500)
        cur.close()
        connection.close()

    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="libraries.toe.html",
        data={
            "title": "Libraries",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "default_lang": default_language,
            "libraries": libs
        },
        hooks=Hooks()
    )


# add library
@libraries.route("/libraries/new", methods=["POST"])
@authorize_web(0)
@db_connection
def add_libraries(*args, permission_level, connection, **kwargs):
    lib_data = request.form
    lib_file = request.files["lib-file"]

    if not lib_file.filename.endswith(".js"):
        return redirect("/libraries?error=upload")
    filename = f"{lib_file.filename[:lib_file.filename.rfind('.')]}-{lib_data['lib-version']}.js"
    try:
        if not os.path.exists(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "libs")):
            os.makedirs(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "libs"))
        with open(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "libs", filename), 'wb') as f:
            lib_file.save(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "libs", filename))
        location = f"/sloth-content/libs/{filename}"

        cur = connection.cursor()
        cur.execute(
            sql.SQL(
                """INSERT INTO sloth_libraries (uuid, name, version, location)  
                VALUES (%s, %s, %s, %s);"""),
            (str(uuid4()), lib_data["lib-name"], lib_data["lib-version"], location)
        )
        connection.commit()
        cur.close()
        connection.close()
    except Exception as e:
        print(traceback.format_exc())
        abort(500)
        cur.close()
        connection.close()

    return redirect("/libraries")


# delete library
@libraries.route("/libraries/delete", methods=["DELETE"])
@authorize_web(0)
@db_connection
def delete_library(*args, permission_level, connection, **kwargs):
    lib_to_delete = request.data

    try:
        cur = connection.cursor()
        cur.execute(
            sql.SQL(
                """SELECT location FROM sloth_libraries WHERE uuid = %s;"""),
            (lib_to_delete["uuid"],)
        )
        location = cur.fetchone()[0]
        cur.execute(
            sql.SQL(
                """DELETE FROM sloth_libraries WHERE uuid = %s;"""),
            (lib_to_delete["uuid"], )
        )
        cur.close()
        os.remove(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "libs", location))
        connection.close()

        response = make_response(json.dumps({
            "deleted": lib_to_delete["uuid"]
        }))
        code = 204
    except Exception as e:
        print(traceback.format_exc())
        abort(500)
        cur.close()
        connection.close()

        response = make_response(json.dumps({
            "error": True
        }))
        code = 500

    response.headers['Content-Type'] = 'application/json'
    return response, code
