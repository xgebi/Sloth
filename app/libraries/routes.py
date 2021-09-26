import psycopg
from flask import abort, request, redirect, current_app, make_response
from app.authorization.authorize import authorize_web
from app.utilities.db_connection import db_connection
from app.toes.hooks import Hooks
from app.toes.toes import render_toe_from_path
from app.post.post_types import PostTypes
from app.utilities import get_default_language
import os
import traceback
import json
from uuid import uuid4

from app.libraries import libraries


# display libraries
@libraries.route("/libraries")
@authorize_web(0)
@db_connection
def show_libraries(permission_level: int, connection: psycopg.Connection):
    """
    Renders page showing libraries in the system

    :param args:
    :param permission_level:
    :param connection:
    :param kwargs:
    :return:
    """
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    default_language = get_default_language(connection=connection)

    try:
        with connection.cursor() as cur:
            cur.execute("""SELECT uuid, name, version, location FROM sloth_libraries;""")
            libs = [{
                "uuid": lib[0],
                "name": lib[1],
                "version": lib[2],
                "location": lib[3]
            } for lib in cur.fetchall()]

    except psycopg.errors.DatabaseError:
        print(traceback.format_exc())
        abort(500)
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
def add_libraries(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
    """
    Endpoint (non-API) to upload new library

    :param args:
    :param permission_level:
    :param connection:
    :param kwargs:
    :return:
    """
    lib_data = request.form
    lib_file = request.files["lib-file"]

    if not lib_file.filename.endswith(".js"):
        return redirect("/libraries?error=upload")
    if lib_file.filename.startswith("."):
        connection.close()
        abort(500)
    filename = f"{lib_file.filename[:lib_file.filename.rfind('.')]}-{lib_data['lib-version']}.js"
    try:
        if not os.path.exists(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "libs")):
            os.makedirs(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "libs"))

        lib_file.save(
            os.path.normpath(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "libs", filename))
        )

        location = f"/sloth-content/libs/{filename}"

        with connection.cursor() as cur:
            cur.execute("""INSERT INTO sloth_libraries (uuid, name, version, location)  VALUES (%s, %s, %s, %s);""",
                        (str(uuid4()), lib_data["lib-name"], lib_data["lib-version"], location))
            connection.commit()
    except psycopg.errors.DatabaseError:
        print(traceback.format_exc())
        connection.close()
        abort(500)
    connection.close()
    return redirect("/libraries")


# delete library
@libraries.route("/libraries/delete", methods=["DELETE"])
@authorize_web(0)
@db_connection
def delete_library(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
    """
    TODO implement with front-end ability to delete a library, until then this is only a stub

    :param args:
    :param permission_level:
    :param connection:
    :param kwargs:
    :return:
    """
    lib_to_delete = json.loads(request.data)

    try:
        with connection.cursor() as cur:
            cur.execute("""SELECT location FROM sloth_libraries WHERE uuid = %s;""",
                        (lib_to_delete["uuid"],)
                        )
            location = cur.fetchone()[0]
            cur.execute("""DELETE FROM sloth_post_libraries WHERE library = %s;""",
                        (lib_to_delete["uuid"],)
                        )
            cur.execute("""DELETE FROM sloth_libraries WHERE uuid = %s;""",
                        (lib_to_delete["uuid"],)
                        )
            connection.commit()
            os.remove(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", "libs", location))

        response = make_response(json.dumps({
            "deleted": lib_to_delete["uuid"]
        }))
        code = 204
    except psycopg.errors.DatabaseError:
        print(traceback.format_exc())
        abort(500)
        response = make_response(json.dumps({
            "error": True
        }))
        code = 500

    connection.close()
    response.headers['Content-Type'] = 'application/json'
    return response, code
