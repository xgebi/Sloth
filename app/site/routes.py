from flask import request, make_response
from flask_cors import cross_origin
import json
import psycopg
import uuid
from time import time
import traceback
from app.utilities.db_connection import db_connection

from app.site import site


@site.route("/api/analytics", methods=["POST"])
@cross_origin()
@db_connection
def update_analytics(*args, connection: psycopg.Connection, **kwargs):
	"""
	API endpoint for gathering analytics from the site

	:param args:
	:param connection:
	:param kwargs:
	:return:
	"""
	analytics_data = request.get_json()
	user_agent = request.user_agent

	try:
		with connection.cursor() as cur:
			cur.execute("""INSERT INTO sloth_analytics (uuid, pathname, last_visit, browser, browser_version, referrer) 
                    VALUES (%s, %s, %s, %s, %s, %s)""",
						(str(uuid.uuid4()), analytics_data["page"], time() * 1000, user_agent.browser,
						 user_agent.version,
						 analytics_data["referrer"]))
			connection.commit()

		response = make_response(json.dumps({"page_recorded": "ok"}))
		code = 200
	except psycopg.errors.DatabaseError as e:
		print("100")
		print(traceback.format_exc())
		response = make_response(json.dumps({"page_recorded": "not ok"}))
		code = 500
	connection.close()

	response.headers['Content-Type'] = 'application/json'
	return response, code
