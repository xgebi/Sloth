from flask import request, abort
from flask_cors import cross_origin
import json
from psycopg2 import sql
import uuid
from time import time
import traceback

from app.utilities.db_connection import db_connection

from app.site import site


@site.route("/api/analytics", methods=["POST"])
@cross_origin()
@db_connection
def update_analytics(*args, connection, **kwargs):	
	analytics_data = request.get_json()

	try:
		cur = connection.cursor()
		cur.execute(
			sql.SQL("INSERT INTO sloth_analytics VALUES (%s, %s, %s)"),
			[str(uuid.uuid4()), analytics_data["page"], time()*1000]
		)
		connection.commit()
	except Exception as e:
		print("100")
		print(traceback.format_exc())
		abort(500)
	
	cur.close()
	connection.close()

	return json.dumps({"page_recorded": "ok"})


@site.route("/api/messages", methods=["POST"])
@cross_origin()
@db_connection
def send_message(*args, connection, **kwargs):	
	message_data = request.get_json()
	try:
		cur = connection.cursor()
		cur.execute(
			sql.SQL("INSERT INTO sloth_messages VALUES (%s, %s, %s, %s, %s, %s)"),
			[str(uuid.uuid4()), message_data["name"], message_data["email"], message_data["body"], time()*1000, 'unread']
		)
		connection.commit()
	except Exception as e:
		print("100")
		print(traceback.format_exc())
		abort(500)
	
	cur.close()
	connection.close()
	return json.dumps({"sent": "ok"})
