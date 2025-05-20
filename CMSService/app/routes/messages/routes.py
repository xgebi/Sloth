import psycopg
from flask import abort, make_response, request, current_app
from app.utilities.db_connection import db_connection
from app.utilities.utilities import get_default_language, get_languages
from app.authorization.authorize import authorize_web, authorize_rest
from app.back_office.post.post_types import PostTypes
from uuid import uuid4
from time import time
import datetime
import json
from flask_cors import cross_origin
from app.toes.hooks import Hooks
import os
from app.toes.toes import render_toe_from_path

from app.routes.messages import messages

@messages.route("/api/messages")
@authorize_rest(0)
@db_connection
def retrieve_message_list(*args, connection: psycopg.Connection, **kwargs):
	"""
	Returns json with list of messages

	:param args:
	:param permission_level:
	:param connection:
	:param kwargs:
	:return:
	"""

	try:
		with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
			cur.execute("""SELECT uuid, sent_date, status 
                FROM sloth_messages WHERE status != 'deleted' ORDER BY sent_date DESC LIMIT 10""")
			message_list = cur.fetchall()
	except psycopg.errors.DatabaseError as e:
		print("db error d")
		abort(500)
	connection.close()

	for message in message_list:
		message.update({
            "sent_date": datetime.datetime.fromtimestamp(float(message['sent_date']) / 1000.0).strftime(
                "%Y-%m-%d %H:%M"),
        })

	return json.dumps(message_list)

@messages.route("/messages")
@authorize_web(0)
@db_connection
def show_message_list(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
	"""
	Renders a page with list of messages

	:param args:
	:param permission_level:
	:param connection:
	:param kwargs:
	:return:
	"""
	post_types = PostTypes()
	post_types_result = post_types.get_post_type_list(connection)

	try:
		with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
			cur.execute("""SELECT uuid, sent_date, status 
                FROM sloth_messages WHERE status != 'deleted' ORDER BY sent_date DESC LIMIT 10""")
			message_list = cur.fetchall()
	except psycopg.errors.DatabaseError as e:
		print("db error d")
		abort(500)

	default_lang = get_default_language(connection=connection)
	languages = get_languages(connection=connection)
	connection.close()

	for message in message_list:
		message.update({
            "sent_date": datetime.datetime.fromtimestamp(float(message['sent_date']) / 1000.0).strftime(
                "%Y-%m-%d %H:%M"),
        })

	return render_toe_from_path(
		path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
		template="message-list.toe.html",
		data={
			"title": "Message",
			"post_types": post_types_result,
			"permission_level": permission_level,
			"default_lang": default_lang,
			"languages": languages,
			"messages": message_list
		},
		hooks=Hooks()
	)


@messages.route("/messages/<msg>")
@authorize_web(0)
@db_connection
def show_message(*args, permission_level: int, connection: psycopg.Connection, msg, **kwargs):
	"""
	Renders a page with a message

	:param args:
	:param permission_level:
	:param connection:
	:param msg:
	:param kwargs:
	:return:
	"""
	post_types = PostTypes()
	post_types_result = post_types.get_post_type_list(connection)

	try:
		with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
			cur.execute("""SELECT sent_date, status FROM sloth_messages WHERE uuid = %s""", (msg,))
			raw_message = cur.fetchone()
			cur.execute("""SELECT name, value FROM sloth_message_fields WHERE message = %s""", (msg,))
			raw_message_fields = cur.fetchall()
			if len(raw_message) > 0:
				cur.execute("""UPDATE sloth_messages SET status = 'read' WHERE uuid = %s""", (msg,))
				connection.commit()
	except psycopg.errors.DatabaseError:
		print("db error e")
		connection.close()
		abort(500)

	default_lang = get_default_language(connection=connection)
	languages = get_languages(connection=connection)

	connection.close()

	message = {
		"sent_date": datetime.datetime.fromtimestamp(float(raw_message['sent_date']) / 1000.0).strftime("%Y-%m-%d"),
		"status": raw_message['status'].strip(),
		"items": [{
			"name": item['name'].strip(),
			"value": item['value'].strip()
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
def delete_message(*args, connection: psycopg.Connection, **kwargs):
	"""
	API endpoint handling deleting a message

	:param args:
	:param connection:
	:param kwargs:
	:return:
	"""

	filled = json.loads(request.data)

	try:
		with connection.cursor() as cur:
			cur.execute("""DELETE FROM sloth_messages WHERE uuid = %s""", (filled["message_uuid"],))
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
def receive_message(*args, connection: psycopg.Connection, **kwargs):
	"""
	Processes received message

	:param args:
	:param connection:
	:param kwargs:
	:return:
	"""
	if request.origin[request.origin.find("//") + 2:] not in current_app.config["ALLOWED_REQUEST_HOSTS"]:
		abort(500)

	filled = json.loads(request.data)
	cur = connection.cursor()
	try:
		msg_id = str(uuid4())
		cur.execute("""INSERT INTO sloth_messages (uuid, sent_date, status) 
            VALUES (%s, %s, %s);""",
					(msg_id, time() * 1000, "unread"))
		cur.execute("""SELECT sff.name FROM sloth_form_fields AS sff 
            INNER JOIN sloth_forms sf on sf.uuid = sff.form WHERE sf.name = %s AND sff.is_required = TRUE;""",
					(filled["formName"],))
		for required in cur.fetchall():
			if required in filled and len(filled[required]) == 0:
				raise Exception("missing required fields")
		for key in filled.keys():
			cur.execute("""INSERT INTO sloth_message_fields (uuid, message, name, value) 
                        VALUES (%s, %s, %s, %s);""",
						(str(uuid4()), msg_id, key, filled[key]))
		connection.commit()
		response = make_response(json.dumps({"messageSaved": True}))
		code = 201
	except Exception as e:
		print(e)
		response = make_response(json.dumps({"messageSaved": False}))
		code = 500

	response.headers['Content-Type'] = 'application/json'
	return response, code
