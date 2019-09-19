from flask import render_template, request, flash, redirect, url_for, current_app, abort

import json
import os
import psycopg2
import uuid
from psycopg2 import sql, errors
import bcrypt
from pathlib import Path
import traceback

from app.utilities.db_connection import db_connection
from app.posts.posts_generator import PostsGenerator

from app.api.registration import registration

@registration.route("/api/register", methods=['POST'])
@db_connection
def initial_settings(*args, connection=None, **kwargs):
	registration_lock_file = Path(os.path.join(os.getcwd(), 'registration.lock'))
	if (registration_lock_file.is_file()):
		return json.dumps({ "error" : "Registration locked"}), 403

	cur = connection.cursor()
	filled = {}
	
	try:
		cur.execute("SELECT count(uuid) FROM sloth_users")
		items = cur.fetchone()
	except errors.UndefinedTable:
		connection.rollback()
		set_tables(connection) 
		items = [0]
	except Exception as e:
		print(traceback.format_exc())
		return json.dumps({"error": "Database connection error"}), 500

	if items[0] > 0:
		return json.dumps({"error": "Registration can be done only once"}), 403

	filled = json.loads(request.data);

	for key,value in filled.items():
		if filled[key] == None:
			return json.dumps({"error" : "Missing values"}), 400

	items = {}

	try:
		cur.execute(
				sql.SQL("SELECT * FROM sloth_users WHERE username = %s"),
				[filled['username']]
			)
		items = cur.fetchall()
	except Exception as e:
		print(traceback.format_exc())
		return json.dumps({ "error": "Database error"}), 500

	if (len(items) == 0):        
		user = {}
		user["uuid"] = str(uuid.uuid4())
		user["username"] = filled["username"]
		user["password"] = bcrypt.hashpw(filled["password"].encode("utf-8"), bcrypt.gensalt(rounds=15)).decode("utf-8")
		user["email"] = filled["email"]
		
		try:
			cur.execute(
				sql.SQL("INSERT INTO sloth_users(uuid, username, display_name, password, email, permissions_level) VALUES (%s, %s, %s, %s, %s, 1)"),
				( user["uuid"], user["username"], user["username"], user["password"], user["email"])
			)
			cur.execute(
				sql.SQL("INSERT INTO sloth_settings VALUES ('sitename', 'Sitename', 'text', 'sloth', %s)"),
				[filled["sitename"]]
			)
			cur.execute(
				sql.SQL("INSERT INTO sloth_settings VALUES ('site_description', 'Description', 'text', 'sloth', %s)"),
				[filled["siteDescription"]]
			)
			cur.execute(
				sql.SQL("INSERT INTO sloth_settings VALUES ('site_url', 'URL', 'text', 'sloth', %s)"),
				[filled["siteUrl"]]
			)
			connection.commit()
		except Exception as e:
			print(traceback.format_exc())
			return json.dumps({ "error": "Database error"}), 500

		cur.close()
		connection.close()

		if not os.path.exists(os.path.join(current_app.config["OUTPUT_PATH"])):
			os.makedirs(os.path.join(current_app.config["OUTPUT_PATH"]))
		if not os.path.exists(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content")):
			os.makedirs(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content"))				
		with open(os.path.join(os.getcwd(), 'registration.lock'), 'w') as f:
			f.write("registration locked")
			
		generator = PostsGenerator(current_app.config)
		generator.regenerate_all()
		return json.dumps({"status": "setup"}), 201
	
	cur.close()
	connection.close()
	
	return json.dumps({"error": "Registration can be done only once"}), 403

def set_tables(con):
	sqls = [sql_file for sql_file in os.listdir(os.path.join(os.getcwd(), "src", "sql", "setup")) if os.path.isfile(os.path.join(os.getcwd(), "src", "sql", "setup", sql_file))]

	cur = con.cursor()
	for filename in sqls:
		with open(os.path.join(os.getcwd(), "src", "sql", "setup", filename)) as f:
			scrpt = str(f.read())
			try:
				cur.execute( scrpt )
				con.commit()
			except Exception as e:
				print(traceback.format_exc())
				abort(500)
	try:
		cur.execute("UPDATE sloth_posts SET author = (SELECT uuid FROM sloth_users LIMIT 1)")
		con.commit()
	except Exception as e:
		print(traceback.format_exc())
		abort(500)
