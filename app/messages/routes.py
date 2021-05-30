from flask import abort, redirect, render_template, make_response, request,current_app
from app.utilities.db_connection import db_connection
from app.utilities import get_default_language, get_languages
from app.authorization.authorize import authorize_web, authorize_rest
from app.post.post_types import PostTypes
from psycopg2 import sql
from uuid import uuid4
from time import time
import datetime
import json
from flask_cors import cross_origin
from app.toes.hooks import Hooks
import os
from app.toes.toes import render_toe_from_path

from app.messages import messages


@messages.route("/messages")
@authorize_web(0)
@db_connection
def show_message_list(*args, permission_level, connection, **kwargs):
    if connection is None:
        return redirect("/database-error")

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    cur = connection.cursor()

    raw_messages = []
    try:
        cur.execute(
            sql.SQL("""SELECT uuid, sent_date, status 
            FROM sloth_messages WHERE status != 'deleted' ORDER BY sent_date DESC LIMIT 10""")
        )
        raw_messages = cur.fetchall()
    except Exception as e:
        print("db error d")
        abort(500)

    cur.close()
    default_language = get_default_language(connection=connection)
    connection.close()

    msgs = []
    for message in raw_messages:
        msgs.append({
            "uuid": message[0],
            "name": message[1],
            "sent_date": datetime.datetime.fromtimestamp(float(message[2])/1000.0).strftime("%Y-%m-%d %H:%M"),
            "status": message[3]
        })

    return render_template(
        "message-list.html",
        post_types=post_types_result,
        permission_level=permission_level,
        messages=msgs,
        default_lang=default_language
    )


@messages.route("/messages/<msg>")
@authorize_web(0)
@db_connection
def show_message(*args, permission_level, connection, msg, **kwargs):
    if connection is None:
        return redirect("/database-error")

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    cur = connection.cursor()

    raw_message_fields = []
    try:
        cur.execute(
            sql.SQL("SELECT sent_date, status FROM sloth_messages WHERE uuid = %s"), (msg, )
        )
        raw_message = cur.fetchone()
        cur.execute(
            sql.SQL("SELECT name, value FROM sloth_message_fields WHERE message = %s"), (msg,)
        )
        raw_message_fields = cur.fetchall()
        if len(raw_message) > 0:
            cur.execute(sql.SQL("UPDATE sloth_messages SET status = 'read' WHERE uuid = %s"), [msg])
            connection.commit()
    except Exception as e:
        print("db error e")
        abort(500)

    default_lang = get_default_language(connection=connection)
    languages = get_languages(connection=connection)

    cur.close()
    connection.close()

    message = {
        "sent_date": datetime.datetime.fromtimestamp(float(raw_message[0])/1000.0).strftime("%Y-%m-%d"),
        "status": raw_message[1].strip(),
        "items": [{
            "name": item[0].strip(),
            "value": item[1].strip()
        } for item in raw_message_fields]
    }

    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="message.toe.html",
        data={
            "title": "Message",
            "post_types": post_types_result,
            "permission_level": permission_level,
            "default_lang": default_lang,
            "languages": languages,
            "message": message
        },
        hooks=Hooks()
    )


@messages.route("/api/messages/delete", methods=["POST", "PUT", "DELETE"])
@authorize_rest(0)
@db_connection
def delete_message(*args, connection, **kwargs):
    if connection is None:
        abort(500)

    filled = json.loads(request.data)
    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL("DELETE FROM sloth_messages WHERE uuid = %s"), [filled["message_uuid"]]
        )
        connection.commit()
        response = make_response(json.dumps({"cleaned": False}))
        code = 204
    except Exception as e:
        print(e)
        response = make_response(json.dumps({"cleaned": False}))
        code = 500

    response.headers['Content-Type'] = 'application/json'
    return response, code


@messages.route("/api/messages/send", methods=["POST"])
@cross_origin()
@db_connection
def receive_message(*args, connection, **kwargs):
    if request.origin[request.origin.find("//") + 2:] not in current_app.config["ALLOWED_REQUEST_HOSTS"]:
        abort(500)
    if connection is None:
        abort(500)

    filled = json.loads(request.data)
    cur = connection.cursor()
    try:
        msg_id = str(uuid4())
        cur.execute(
            sql.SQL("""INSERT INTO sloth_messages (uuid, sent_date, status) 
            VALUES (%s, %s, %s);"""),
            (msg_id, time() * 1000, "unread")
        )
        cur.execute(
            sql.SQL("""SELECT sff.name FROM sloth_form_fields AS sff 
            INNER JOIN sloth_forms sf on sf.uuid = sff.form WHERE sf.name = %s AND sff.is_required = TRUE;"""),
            (filled["formName"], )
        )
        for required in cur.fetchall():
            if required in filled and len(filled[required]) == 0:
                raise Exception("missing required fields")
        for key in filled.keys():
            cur.execute(
                sql.SQL("""INSERT INTO sloth_message_fields (uuid, message, name, value) 
                        VALUES (%s, %s, %s, %s);"""),
                (str(uuid4()), msg_id, key, filled[key])
            )
        connection.commit()
        response = make_response(json.dumps({"messageSaved": True}))
        code = 201
    except Exception as e:
        print(e)
        response = make_response(json.dumps({"messageSaved": False}))
        code = 500

    response.headers['Content-Type'] = 'application/json'
    return response, code
