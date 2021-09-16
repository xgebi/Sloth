from flask import request, abort, make_response
from flask_cors import cross_origin
import json
from psycopg2 import sql
import uuid
from time import time
import traceback

from app.utilities.db_connection import db_connection_legacy

from app.site import site


@site.route("/api/analytics", methods=["POST"])
@cross_origin()
@db_connection_legacy
def update_analytics(*args, connection, **kwargs):
    analytics_data = request.get_json()
    user_agent = request.user_agent

    try:
        cur = connection.cursor()
        cur.execute(
            sql.SQL(
                """INSERT INTO sloth_analytics (uuid, pathname, last_visit, browser, browser_version, referrer) 
				VALUES (%s, %s, %s, %s, %s, %s)"""),
            (str(uuid.uuid4()), analytics_data["page"], time() * 1000, user_agent.browser, user_agent.version,
             analytics_data["referrer"])
        )
        connection.commit()
        cur.close()
        connection.close()

        response = make_response(json.dumps({"page_recorded": "ok"}))
        code = 200
    except Exception as e:
        print("100")
        print(traceback.format_exc())
        response = make_response(json.dumps({"page_recorded": "not ok"}))
        code = 500

    response.headers['Content-Type'] = 'application/json'
    return response, code


@site.route("/api/messages", methods=["POST"])
@cross_origin()
@db_connection_legacy
def send_message(*args, connection, **kwargs):
    message_data = request.get_json()
    try:
        cur = connection.cursor()
        cur.execute(
            sql.SQL("INSERT INTO sloth_messages VALUES (%s, %s, %s, %s, %s, %s)"),
            [str(uuid.uuid4()), message_data["name"], message_data["email"], message_data["body"], time() * 1000,
             'unread']
        )
        connection.commit()
        cur.close()
        connection.close()
        response = make_response(json.dumps({"page_recorded": "ok"}))
        code = 200
    except Exception as e:
        print("100")
        print(traceback.format_exc())
        response = make_response(json.dumps({"page_recorded": "not ok"}))
        code = 500

    response.headers['Content-Type'] = 'application/json'
    return response, code
