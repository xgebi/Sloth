from flask import request, make_response
from flask_cors import cross_origin
import json
import psycopg
import uuid
from time import time
import traceback
from app.utilities.db_connection import db_connection

from app.routes.site import site


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

	browser = analytics_data["userAgent"]
	browser_lower = browser.lower()
	browser_version = ""
	if "firefox" in browser_lower:
		browser = "Firefox"
		browser_version = analytics_data["userAgent"][analytics_data["userAgent"].rfind("/") + 1:]
	elif "chrome" in browser_lower and "safari" in browser_lower:
		if "googlebot" in browser_lower:
			browser = "Bot - Google/Chrome"
		elif "bingbot" in browser_lower:
			browser = "Bot - Bingbot/Chrome"
		else:
			browser = "Chrome"
		browser_version = analytics_data["userAgent"][analytics_data["userAgent"].find("Chrome"):analytics_data["userAgent"].find(" Safari")].split("/")[1]
	elif "chrome" not in browser_lower and "safari" in browser_lower:
		browser = "Safari"
		browser_version = analytics_data["userAgent"][analytics_data["userAgent"].find("Version"):analytics_data["userAgent"].find(" Safari")].split("/")[1]
	elif "ahrefsbot" in browser_lower:
		browser = "Bot - AhrefsBot"
		tail_end = analytics_data["userAgent"][analytics_data["userAgent"].find("AhrefsBot"):]
		browser_version = tail_end[:tail_end.find("; ")]

	try:
		with connection.cursor() as cur:
			cur.execute("""INSERT INTO sloth_analytics (uuid, pathname, last_visit, browser, browser_version, referrer, source) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
						(str(uuid.uuid4()), analytics_data["page"], time() * 1000, browser,
						 browser_version,
						 analytics_data["referrer"], analytics_data["source"]))
			connection.commit()

		response = make_response(json.dumps({"page_recorded": "ok"}))
		code = 200
	except psycopg.errors.DatabaseError as e:
		print("100")
		print(e)
		traceback.print_exc()
		response = make_response(json.dumps({"page_recorded": "not ok"}))
		code = 500
	connection.close()

	response.headers['Content-Type'] = 'application/json'
	return response, code
