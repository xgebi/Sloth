from flask import abort, request, make_response
from app.authorization.authorize import authorize_web
from app.utilities.db_connection import db_connection
from app.toes.hooks import Hooks
from app.toes.toes import render_toe_from_path
from app.back_office.post.post_types import PostTypes
from app.utilities.utilities import get_default_language, get_languages
import psycopg
import os
import traceback
import json
from uuid import uuid4

from app.forms import forms


# display form page
@forms.route("/forms")
@authorize_web(0)
@db_connection
def show_forms(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
    """
    Renders page which shows list of forms

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
        with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
            langs = get_languages(connection=connection, as_list=False)

            cur.execute(
                """SELECT uuid, name, lang as lang_id FROM sloth_forms;"""
            )
            forms_list = [form.update({
                "lang_name": langs[form['lang_id']]["long_name"]
            }) for form in cur.fetchall()]

    except psycopg.errors.DatabaseError as e:
        print(traceback.format_exc())
        abort(500)
    connection.close()
    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="forms.toe.html",
        data={
            "title": "Libraries",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "default_lang": default_language,
            "forms": forms_list,
            "new": str(uuid4())
        },
        hooks=Hooks()
    )


@forms.route("/forms/<form_id>")
@authorize_web(0)
@db_connection
def show_form(*args, permission_level: int, connection: psycopg.Connection, form_id: str, **kwargs):
    """
    Show page where human can edit the form

    :param args:
    :param permission_level:
    :param connection:
    :param form_id:
    :param kwargs:
    :return:
    """
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)
    default_language = get_default_language(connection=connection)
    languages = get_languages(connection=connection)
    try:
        with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(
                """SELECT uuid, name, lang
                    FROM sloth_forms WHERE uuid = %s;""",
                (form_id,)
            )
            raw_form = cur.fetchone()
            if raw_form is None:
                is_new = True
                form_language = ""
                form_name = ""
            else:
                is_new = False
                form_language = raw_form['lang']
                form_name = raw_form['name']

            cur.execute("""SELECT uuid, name, position, is_childless, type, is_required, label
                    FROM sloth_form_fields WHERE form = %s;""",
                        (form_id,)
                        )

            fields = cur.fetchall()
            fields.sort(key=lambda form: form.get("position"))

    except psycopg.errors.DatabaseError as e:
        print(traceback.format_exc())
        abort(500)
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
def save_form(*args, permission_level: int, connection: psycopg.Connection, form_id: str, **kwargs):
    """
    Processes saving the form

    :param args:
    :param permission_level:
    :param connection:
    :param form_id:
    :param kwargs:
    :return:
    """
    filled = json.loads(request.data)

    try:
        with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute("""DELETE FROM sloth_form_fields WHERE form = %s;""",
                        (form_id,)
                        )
            cur.execute("""SELECT uuid FROM sloth_forms WHERE uuid = %s;""",
                        (form_id,)
                        )
            if len(cur.fetchall()) == 0:
                cur.execute("""INSERT INTO sloth_forms (uuid, name, lang) 
                                            VALUES (%s, %s, %s);""",
                            (form_id, filled["formName"], filled["language"])
                            )
            else:
                cur.execute("""UPDATE sloth_forms SET name = %s, lang = %s WHERE uuid = %s;""",
                            (filled["formName"], filled["language"], form_id))
            connection.commit()
            for field in filled["fields"]:
                cur.execute("""INSERT INTO sloth_form_fields (uuid, name, form, position, type, is_required, label) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s);""",
                            (str(uuid4()), field["name"], form_id, int(field["position"]), field["type"],
                             bool(field["isRequired"]),
                             field["label"])
                            )
        connection.commit()
        response = make_response(json.dumps({"saved": form_id}))
        code = 204
    except Exception as e:
        response = make_response(json.dumps({"notSaved": form_id}))
        code = 500

    connection.close()
    response.headers['Content-Type'] = 'application/json'
    return response, code


# delete form
@forms.route("/api/forms/<form_id>/delete", methods=["POST", "DELETE"])
@authorize_web(0)
@db_connection
def delete_form(*args, permission_level: int, connection: psycopg.Connection, form_id: str, **kwargs):
    """
    API endpoint processes form deletion

    :param args:
    :param permission_level:
    :param connection:
    :param form_id:
    :param kwargs:
    :return:
    """
    try:
        with connection.cursor() as cur:
            cur.execute("""DELETE FROM sloth_form_fields WHERE form = %s;""",
                        (form_id,)
                        )
            cur.execute("""DELETE FROM sloth_forms WHERE uuid = %s;""",
                        (form_id,)
                        )
            connection.commit()
        response = make_response(json.dumps({"deleted": form_id}))
        code = 204
    except Exception as e:
        response = make_response(json.dumps({"notDeleted": form_id}))
        code = 500

    connection.close()
    response.headers['Content-Type'] = 'application/json'
    return response, code
