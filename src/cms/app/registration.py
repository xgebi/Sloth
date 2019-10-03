class Registration:
	connection = {}

	def __init__(self, connection):
		self.connection = connection

	def initial_settings(self, *args, **kwargs):
		registration_lock_file = Path(os.path.join(os.getcwd(), 'registration.lock'))
		if (registration_lock_file.is_file()):
			return {"error": "Registration locked", "status": 403}

		cur = self.connection.cursor()
		filled = {}
		
		try:
			cur.execute("SELECT count(uuid) FROM sloth_users")
			items = cur.fetchone()
		except errors.UndefinedTable:
			self.connection.rollback()
			result = self.set_tables() 
			if (result["error"]):
				return result
			items = [0]
		except Exception as e:
			print(traceback.format_exc())
			return {"error": "Database connection error", "status": 500}

		if items[0] > 0:
			return {"error": "Registration can be done only once", "status": 403}

		filled = json.loads(request.data);

		for key,value in filled.items():
			if filled[key] == None:
				return {"error" : "Missing values", "status": 400}

		items = {}

		try:
			cur.execute(
					sql.SQL("SELECT * FROM sloth_users WHERE username = %s"),
					[filled['username']]
				)
			items = cur.fetchall()
		except Exception as e:
			print(traceback.format_exc())
			return { "error": "Database error", "status": 500}

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
				self.connection.commit()
			except Exception as e:
				print(traceback.format_exc())
				return { "error": "Database error", "status": 500}

			cur.close()
			self.connection.close()

			if not os.path.exists(os.path.join(current_app.config["OUTPUT_PATH"])):
				os.makedirs(os.path.join(current_app.config["OUTPUT_PATH"]))
			if not os.path.exists(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content")):
				os.makedirs(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content"))				
			with open(os.path.join(os.getcwd(), 'registration.lock'), 'w') as f:
				f.write("registration locked")
				
			generator = PostsGenerator(current_app.config)
			generator.regenerate_all()
			return {"state": "ok", "status": 201}
		
		cur.close()
		self.connection.close()
		
		return {"error": "Registration can be done only once", "status": 403}

	def set_tables(self):
		sqls = [sql_file for sql_file in os.listdir(os.path.join(os.getcwd(), "src", "sql", "setup")) if os.path.isfile(os.path.join(os.getcwd(), "src", "sql", "setup", sql_file))]

		cur = self.connection.cursor()
		for filename in sqls:
			with open(os.path.join(os.getcwd(), "src", "sql", "setup", filename)) as f:
				scrpt = str(f.read())
				try:
					cur.execute( scrpt )
					self.connection.commit()
				except Exception as e:
					print(traceback.format_exc())
					return { "error": "Database error", "status": 500}
		try:
			cur.execute("UPDATE sloth_posts SET author = (SELECT uuid FROM sloth_users LIMIT 1)")
			self.connection.commit()
		except Exception as e:
			print(traceback.format_exc())
			return { "error": "Database error", "status": 500}
		return {"state": "ok"}