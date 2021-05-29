from flask import abort, request, redirect, current_app, make_response
from app.authorization.authorize import authorize_web
from app.utilities.db_connection import db_connection
from app.toes.hooks import Hooks
from app.toes.toes import render_toe_from_path
from app.post.post_types import PostTypes
from app.utilities import get_default_language, get_languages
from psycopg2 import sql
import os
import traceback
import json
from uuid import uuid4

from app.forms import forms


# display form page
@forms.route("/forms")
@authorize_web(0)
@db_connection
def show_forms(*args, permission_level, connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    default_language = get_default_language(connection=connection)

    try:
        cur = connection.cursor()

        langs = get_languages(connection=connection, as_list=False)

        cur.execute(
            sql.SQL(
                """SELECT uuid, name, lang 
                FROM sloth_forms;""")
        )
        forms = [{
            "uuid": form[0],
            "name": form[1],
            "lang_id": form[2],
            "lang_name": langs[form[2]]["long_name"]
        } for form in cur.fetchall()]

        cur.close()
        connection.close()
    except Exception as e:
        print(traceback.format_exc())
        abort(500)
        cur.close()
        connection.close()

    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="forms.toe.html",
        data={
            "title": "Libraries",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "default_lang": default_language,
            "forms": forms,
            "new": str(uuid4())
        },
        hooks=Hooks()
    )


@forms.route("/forms/<form_id>")
@authorize_web(0)
@db_connection
def show_form(*args, permission_level, connection, form_id: str, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    default_language = get_default_language(connection=connection)
    languages = get_languages(connection=connection)
    try:
        cur = connection.cursor()

        cur.execute(
            sql.SQL(
                """SELECT uuid, name, slug, lang
                FROM sloth_forms WHERE uuid = %s;"""),
            (form_id,)
        )
        raw_form = cur.fetchone()
        if raw_form is None:
            is_new = True
            form_language = ""
            form_name = ""
        else:
            is_new = False
            form_language = raw_form[3]
            form_name = raw_form[1]

        cur.execute(
            sql.SQL(
                """SELECT uuid, name, position
                FROM sloth_form_fields WHERE form = %s;"""),
            (form_id, )
        )

        fields = [{
            "uuid": field[0],
            "name": field[1],
            "position": field[2],
        } for field in cur.fetchall()]
        fields.sort(key=lambda form: form.get("position"))

        cur.close()
        connection.close()
    except Exception as e:
        print(traceback.format_exc())
        abort(500)
        cur.close()
        connection.close()

    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="form.toe.html",
        data={
            "title": "Create form" if is_new else "Edit form",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "default_lang": default_language,
            "form_id": form_id,
            "fields": fields,
            "form_name": form_name,
            "form_language": form_language,
            "new": is_new,
            "languages": languages
        },
        hooks=Hooks()
    )


# save form
@forms.route("/api/forms/<form_id>/save", methods=["POST"])
@authorize_web(0)
@db_connection
def save_form(*args, permission_level, connection, form_id: str, **kwargs):
    if connection is None:
        abort(500)

    fields = json.loads(request.data)

    try:
        cur = connection.cursor()
        cur.execute(
            sql.SQL("""DELETE FROM sloth_form_fields WHERE form = %s;"""),
            (form_id, )
        )
        cur.execute(
            sql.SQL("""SELECT uuid FROM sloth_forms WHERE uuid = %s;"""),
            (form_id, )
        )
        if len(cur.fetchall()) == 0:
            cur.execute(
                sql.SQL("""INSERT INTO sloth_forms (uuid, name, slug, lang) 
                                        VALUES (%s, %s, %s, %s);"""),
                (form_id, fields["name"], fields["slug"], fields["lang"])
            )
            connection.commit()
        for field in fields:
            cur.execute(
                sql.SQL("""INSERT INTO sloth_form_fields (uuid, name, form, position) 
                            VALUES (%s, %s, %s, %s);"""),
                (field["uuid"], field["name"], form_id, field["position"])
            )
        connection.commit()
        response = make_response(json.dumps({"deleted": form_id}))
        code = 204
    except Exception as e:
        response = make_response(json.dumps({"notDeleted": form_id}))
        code = 500

    cur.close()
    connection.close()
    response.headers['Content-Type'] = 'application/json'
    return response, code


# delete form
@forms.route("/api/forms/<form_id>/delete", methods=["POST", "DELETE"])
@authorize_web(0)
@db_connection
def delete_form(*args, permission_level, connection, form_id: str, **kwargs):
    if connection is None:
        abort(500)

    try:
        cur = connection.cursor()
        cur.execute(
            sql.SQL("""DELETE FROM sloth_form_fields WHERE form = %s;"""),
            (form_id, )
        )
        cur.execute(
            sql.SQL("""DELETE FROM sloth_forms WHERE uuid = %s;"""),
            (form_id,)
        )
        connection.commit()
        response = make_response(json.dumps({"deleted": form_id}))
        code = 204
    except Exception as e:
        response = make_response(json.dumps({"notDeleted": form_id}))
        code = 500
    cur.close()
    connection.close()
    response.headers['Content-Type'] = 'application/json'
    return response, code


