# app/__init__.py
import os
from flask import Flask, request, redirect, url_for
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import os
from pathlib import Path

bcrypt = Bcrypt()


def create_app():  # dev, test, or prod

	app = Flask(__name__)
	cors = CORS(app)
	configuration = os.path.join(os.getcwd(), 'config', f'{os.environ["FLASK_ENV"]}.py')

	app.config.from_pyfile(configuration)
	app.config["THEMES_PATH"] = os.path.join(os.getcwd(), 'themes')
	app.config["TEMPLATES_PATH"] = os.path.join(os.getcwd(), 'src', 'cms', 'app', 'templates')
	app.config['CORS_HEADERS'] = 'Content-Type'


	bcrypt.init_app(app)

	@app.before_request
	def before_first_request():
		registration_lock_file = Path(os.path.join(os.getcwd(), 'registration.lock'))
		if not (request.path.startswith('/api') or request.path.startswith('/registration') or request.path.startswith('/design') or request.path.startswith('/static')) and not registration_lock_file.is_file():
			return redirect('/registration')

	from app.errors import errors
	app.register_blueprint(errors)

	from app.api.dashboard import dashboard
	app.register_blueprint(dashboard)

	from app.api.post import post as post_api
	app.register_blueprint(post_api)

	from app.api.themes import themes
	app.register_blueprint(themes)

	from app.api.content_management import content_management
	app.register_blueprint(content_management)

	from app.web.root import root
	app.register_blueprint(root)

	from app.web.registration import registration
	app.register_blueprint(registration)

	from app.web.login import login
	app.register_blueprint(login)

	from app.web.dashboard import dashboard as dash
	app.register_blueprint(dash)

	from app.web.settings import settings as web_settings
	app.register_blueprint(web_settings)

	from app.web.settings.themes import settings_themes
	app.register_blueprint(settings_themes)

	from app.web.settings.users import settings_users
	app.register_blueprint(settings_users)

	from app.web.post import post
	app.register_blueprint(post)

	from app.web.design import design
	app.register_blueprint(design)

	from app.web.messages import messages
	app.register_blueprint(messages)

	from app.api.site import site
	app.register_blueprint(site)


	return app