from app import create_app

if __name__ == '__main__':
	flask_app = create_app()

	with flask_app.app_context():
		flask_app.run()

# pip install --user flask flask_cors bcrypt flask_bcrypt psycopg2 python-dateutil pytz Authlib