import re
from typing import Dict

from flask import current_app
import os
import psycopg
from pathlib import Path
import uuid
import bcrypt
import traceback

from app.authorization.user import test_password
from app.back_office.post.post_generator import PostGenerator


class Register:
	connection = {}

	def __init__(self, connection: psycopg.connection):
		self.connection = connection

	def initial_settings(self, *args, filled: Dict = {}, **kwargs):
		registration_lock_file = Path(os.path.join(os.getcwd(), 'registration.lock'))
		if registration_lock_file.is_file():
			print("Registration locked")
			return {"error": "Registration locked", "status": 403}

		try:
			with self.connection.cursor() as cur:
				cur.execute("SELECT count(uuid) FROM sloth_users")
				items = cur.fetchone()
		except psycopg.errors.UndefinedTable:
			self.connection.rollback()
			result = self.set_tables()

			if result.get("error") is not None:
				self.de_setup()
				return result
			items = [0]
		except Exception as e:
			self.de_setup()
			print(e)
			traceback.print_exc()
			return {"error": "database", "status": 500}

		if items[0] > 0:
			self.de_setup()
			print("Registration can be done only once")
			return {"error": "Registration can be done only once", "status": 403}

		for key, value in filled.items():
			if filled[key] is None or len(value) == 0:
				self.de_setup()
				return {"error": "missing", "status": 400}

		try:
			with self.connection.cursor() as cur:
				cur.execute("SELECT * FROM sloth_users WHERE username = %s",
							(filled['username'],))
				items = cur.fetchall()
		except Exception as e:
			print(e)
			traceback.print_exc()
			self.de_setup()
			return {"error": "database", "status": 500}

		if len(items) == 0:
			if not test_password(filled["password"]):
				self.de_setup()
				return {"error": "password"}
			user = {"uuid": str(uuid.uuid4()), "username": filled["username"],
					"password": bcrypt.hashpw(filled["password"].encode("utf-8"), bcrypt.gensalt(rounds=14)).decode(
						"utf-8")}

			try:
				with self.connection.cursor() as cur:
					cur.execute(
						"""INSERT INTO sloth_users(uuid, username, display_name, password, permissions_level) 
							VALUES (%s, %s, %s, %s, 1)""",
						(user["uuid"], user["username"], user["username"], user["password"]))
					cur.execute("INSERT INTO sloth_settings VALUES ('sitename', 'Sitename', 'text', 'sloth', %s)",
								(filled["sitename"],))
					cur.execute("INSERT INTO sloth_settings VALUES ('site_timezone', 'Timezone', 'text', 'sloth', %s)",
								(filled["timezone"],))
					cur.execute(
						"INSERT INTO sloth_settings VALUES ('site_description', 'Description', 'text', 'sloth', '')")
					cur.execute("INSERT INTO sloth_settings VALUES ('site_url', 'URL', 'text', 'sloth', %s)",
								(filled["url"],))
					cur.execute("INSERT INTO sloth_settings VALUES ('api_url', 'URL', 'text', 'sloth', %s)",
								(filled["admin-url"],))

					lang_uuid = str(uuid.uuid4())

					cur.execute(
						"""INSERT INTO sloth_language_settings VALUES (%s, %s, %s)""",
						(lang_uuid, filled["main-language-short"], filled["main-language-long"],))

					cur.execute(
						"INSERT INTO sloth_settings VALUES ('main_language', 'Main language', 'text', 'sloth', %s)",
						(lang_uuid,))

					self.connection.commit()
			except Exception as e:
				print(e)
				traceback.print_exc()
				return {"error": "Database error", "status": 500}

			self.set_data()

			if not os.path.exists(os.path.join(current_app.config["OUTPUT_PATH"])):
				os.makedirs(os.path.join(current_app.config["OUTPUT_PATH"]))
			if not os.path.exists(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content")):
				os.makedirs(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content"))
			with open(os.path.join(os.getcwd(), 'registration.lock'), 'w') as f:
				f.write("registration locked")

			generator = PostGenerator(connection=self.connection)
			if generator.run(everything=True):
				return {"state": "ok", "status": 201}
			return {"status": 500, "error": "Generating post"}

		self.connection.close()

		print("Registration can be done only once")
		return {"error": "Registration can be done only once", "status": 403}

	def set_tables(self):
		sqls = [sql_file for sql_file in os.listdir(os.path.join(os.getcwd(), "database", "setup")) if
				os.path.isfile(os.path.join(os.getcwd(), "database", "setup", sql_file))]

		with self.connection.cursor() as cur:
			for filename in sorted(sqls):
				with open(os.path.join(os.getcwd(), "database", "setup", filename)) as f:
					script = str(f.read())
					try:
						cur.execute(script)
						self.connection.commit()
					except Exception as e:
						print("hihi")
						print(e)
						traceback.print_exc()
						return {"error": "Database error", "status": 500}
		return {"state": "ok"}

	def set_data(self):
		sqls = [sql_file for sql_file in os.listdir(os.path.join(os.getcwd(), "database", "setup_data")) if
				os.path.isfile(os.path.join(os.getcwd(), "database", "setup_data", sql_file))]

		with self.connection.cursor() as cur:
			for filename in sorted(sqls):
				with open(os.path.join(os.getcwd(), "database", "setup_data", filename)) as f:
					script = str(f.read())
				try:
					cur.execute(script)
					self.connection.commit()
				except Exception as e:
					print(script)
					print(e)
					traceback.print_exc()
					return {"error": "Database error", "status": 500}
			try:
				cur.execute("""SELECT name, standalone FROM sloth_localizable_strings;""")
				localizable = cur.fetchall()
				cur.execute("""SELECT uuid FROM sloth_post_types;""")
				post_types = [id[0] for id in cur.fetchall()]
				for item in localizable:
					if item[1]:
						cur.execute("""INSERT INTO sloth_localized_strings (uuid, name, content, lang, post_type) 
                        VALUES (%s, %s, %s,
                        (SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language'), %s)""",
									(str(uuid.uuid4()), item[0], '', None))
					else:
						for post_type in post_types:
							cur.execute("""INSERT INTO sloth_localized_strings (uuid, name, content, lang, post_type) 
                                                    VALUES (%s, %s, %s,
                                                    (SELECT settings_value FROM sloth_settings 
                                                    WHERE settings_name = 'main_language'), %s)""",
										(str(uuid.uuid4()), item[0], '', post_type))
				self.connection.commit()
			except Exception as e:
				print(e)
				traceback.print_exc()
				return {"error": "Database error", "status": 500}
		return {"state": "ok"}

	def de_setup(self):
		sqls = [sql_file for sql_file in os.listdir(os.path.join(os.getcwd(), "database", "de-setup")) if
				os.path.isfile(os.path.join(os.getcwd(), "database", "de-setup", sql_file))]

		with self.connection.cursor() as cur:
			for filename in sorted(sqls):
				with open(os.path.join(os.getcwd(), "database", "de-setup", filename)) as f:
					script = str(f.read())
				try:
					cur.execute(script)
					self.connection.commit()
				except Exception as e:
					print(script)
					print(e)
					traceback.print_exc()
					return {"error": "Database error", "status": 500}
		return {"state": "reverted"}
