from flask import request, abort, redirect, render_template, make_response, current_app
from flask_cors import cross_origin
from psycopg2 import sql
import json
import uuid
import os
from app.post.post_types import PostTypes
from app.utilities.db_connection import db_connection_legacy
from app.utilities import get_default_language
from app.authorization.authorize import authorize_web
from app.toes.toes import render_toe_from_path
from app.toes.hooks import Hooks
from app.utilities import get_languages

from app.mock_endpoints import mock_endpoints


@mock_endpoints.route("/mock-endpoints")
@authorize_web(0)
@db_connection_legacy
def show_endpoints_list(*args, permission_level, connection, **kwargs):
    if connection is None:
        abort(500)
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    cur = connection.cursor()
    temp_endpoints_list = []
    try:
        cur.execute(
            sql.SQL("""SELECT uuid, path FROM sloth_mock_endpoints ORDER BY path DESC;""")
        )
        temp_endpoints_list = cur.fetchall()
    except Exception as e:
        print(e)
        abort(500)

    cur.close()
    default_language = get_default_language(connection=connection)
    connection.close()
    endpoints_list = []
    for endpoint in temp_endpoints_list:
        endpoints_list.append({
            "uuid": endpoint[0],
            "path": endpoint[1]
        })

    return render_template(
        "mock-endpoints-list.html",
        post_types=post_types_result,
        permission_level=permission_level,
        endpoints_list=endpoints_list,
        default_lang=default_language
                           )


@mock_endpoints.route("/mock-endpoints/<endpoint>", methods=["GET"])
@authorize_web(0)
@db_connection_legacy
def show_endpoint(*args, permission_level, connection, endpoint, **kwargs):
    if connection is None:
        abort(500)
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    default_lang = get_default_language(connection=connection)
    languages = get_languages(connection=connection, as_list=True)

    cur = connection.cursor()
    temp_endpoint_result = {}
    try:
        cur.execute(
            sql.SQL("""SELECT uuid, path, data, content_type FROM sloth_mock_endpoints WHERE uuid = %s"""),
            [endpoint]
        )
        temp_endpoint_result = cur.fetchone()
    except Exception as e:
        print(e)
        abort(500)

    cur.close()
    connection.close()

    endpoint_result = {
        "uuid": temp_endpoint_result[0],
        "path": temp_endpoint_result[1],
        "data": temp_endpoint_result[2],
        "content_type": temp_endpoint_result[3],
        "new": False
    }

    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="mock-endpoint.toe.html",
        data={
            "title": "List of media",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "default_lang": default_lang,
            "languages": languages,
            "endpoint": {
                "uuid": str(uuid.uuid4()),
                "new": True
            },
            "endpoint": endpoint_result
        },
        hooks=Hooks()
    )


@mock_endpoints.route("/api/mock-endpoints/<endpoint>/delete", methods=["DELETE"])
@authorize_web(0)
@db_connection_legacy
def delete_endpoint(*args, permission_level, connection, endpoint, **kwargs):
    if connection is None:
        abort(500)

    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL("""DELETE FROM sloth_mock_endpoints WHERE uuid = %s"""),
            [endpoint]
        )
        connection.commit()
    except Exception as e:
        print(e)
        abort(500)

    cur.close()
    connection.close()

    return json.dumps({"endpoint": "deleted"}), 204


@mock_endpoints.route("/mock-endpoints/new", methods=["GET"])
@authorize_web(0)
@db_connection_legacy
def show_new_endpoint(*args, permission_level, connection, **kwargs):
    if connection is None:
        abort(500)
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    default_lang = get_default_language(connection=connection)
    languages = get_languages(connection=connection)

    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="mock-endpoint.toe.html",
        data={
            "title": "List of media",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "default_lang": default_lang,
            "languages": languages,
            "endpoint": {
                "uuid": str(uuid.uuid4()),
                "new": True
            }
        },
        hooks=Hooks()
    )


@mock_endpoints.route("/mock-endpoints/<endpoint_id>/save", methods=["POST", "PUT"])
@authorize_web(0)
@db_connection_legacy
def save_endpoint(*args, permission_level, connection, endpoint_id, **kwargs):
    if connection is None:
        abort(500)

    filled = request.form
    for key in filled.keys():
        if len(filled[key]) == 0:
            abort(400)

    cur = connection.cursor()
    try:
        if filled["new"].lower() == "true":
            cur.execute(
                sql.SQL("""INSERT INTO sloth_mock_endpoints VALUES (%s, %s, %s, %s)"""),
                (endpoint_id, filled["path"], filled["data"], filled["content_type"])
            )
        else:
            cur.execute(
                sql.SQL("""UPDATE sloth_mock_endpoints SET path = %s, data = %s, content_type = %s WHERE uuid = %s"""),
                (filled["path"], filled["data"], filled["content_type"], endpoint_id)
            )
        connection.commit()
    except Exception as e:
        abort(500)

    cur.close()
    connection.close()

    return redirect(f"/mock-endpoints/{endpoint_id}")


@mock_endpoints.route("/api/mock/<path>", methods=["GET"])
@cross_origin()
@db_connection_legacy
def get_endpoint(*args, connection, path, **kwargs):
    if request.origin[request.origin.find("//") + 2: ] not in current_app.config["ALLOWED_REQUEST_HOSTS"]:
        abort(500)
    if connection is None:
        abort(500)

    result = ""
    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL("""SELECT data, content_type FROM sloth_mock_endpoints WHERE path = %s;"""),
            [path]
        )
        temp_result = cur.fetchone()
        if temp_result is not None and len(temp_result) >= 1:
            result = temp_result[0]
            content_type = temp_result[1]
        else:
            result = json.dumps({"error": "Missing data"})
    except Exception as e:
        print(e)
        abort(500)

    cur.close()
    connection.close()

    response = make_response(result)
    response.headers['Content-Type'] = content_type

    return response
