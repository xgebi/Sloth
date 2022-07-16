# app/__init__.py
import os
import threading
from flask import Flask, request, redirect
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from pathlib import Path
from uuid import uuid4

from app.scheduler import publish_posts
from app.toes.hooks import Hooks, Hook

bcrypt = Bcrypt()


class Dummy:
	def __init__(self):
		self.name = "Dummy bot"


def create_app():  # dev, test, or prod

	app = Flask(__name__)
	cors = CORS(app)
	app.config.from_mapping(
		SECRET_KEY='dev',
		THREAD_ID=uuid4()
	)

	app.config.from_pyfile(os.path.join(os.getcwd(), 'config', f'{os.environ["FLASK_ENV"]}.py'))
	app.config["THEMES_PATH"] = os.path.join(os.getcwd(), 'themes')
	app.config["TEMPLATES_PATH"] = os.path.join(os.getcwd(), 'src', 'cms', 'app', 'templates')
	app.config['CORS_HEADERS'] = 'Content-Type'

	bcrypt.init_app(app)

	@app.before_request
	def before_first_request():
		registration_lock_file = Path(os.path.join(os.getcwd(), 'registration.lock'))
		if not (request.path.startswith('/api') or request.path.startswith('/registration') or request.path.startswith(
				'/design') or request.path.startswith('/static')) and not registration_lock_file.is_file():
			return redirect('/registration')

	if os.environ["FLASK_ENV"] != "development":
		@app.errorhandler(500)
		def internal_error(error):
			return "500 error", 500

	@app.errorhandler(403)
	def internal_error(error):
		return "403 error", 403

	@app.errorhandler(404)
	def not_found(error):
		return "404 error", 404

	from app.api.content_management import content_management
	app.register_blueprint(content_management)

	from app.root import root
	app.register_blueprint(root)

	from app.registration import registration
	app.register_blueprint(registration)

	from app.routes.login import login
	app.register_blueprint(login)

	from app.dashboard import dashboard
	app.register_blueprint(dashboard)

	from app.dashboard.analytics import analytics
	app.register_blueprint(analytics)

	from app.settings import settings
	app.register_blueprint(settings)

	from app.settings.themes import settings_themes
	app.register_blueprint(settings_themes)

	from app.settings.themes.menu import menu
	app.register_blueprint(menu)

	from app.settings.content import content
	app.register_blueprint(content)

	from app.settings.users import settings_users
	app.register_blueprint(settings_users)

	from app.routes.post import post
	app.register_blueprint(post)

	from app.messages import messages
	app.register_blueprint(messages)

	from app.site import site
	app.register_blueprint(site)

	from app.routes.post_type import post_type
	app.register_blueprint(post_type)

	from app.forms import forms
	app.register_blueprint(forms)

	from app.api.taxonomy import taxonomy as taxonomy_api
	app.register_blueprint(taxonomy_api)

	from app.media import media
	app.register_blueprint(media)

	from app.mock_endpoints import mock_endpoints
	app.register_blueprint(mock_endpoints)

	from app.settings.language_settings import language_settings
	app.register_blueprint(language_settings)

	from app.settings.localized_settings import localized_settings
	app.register_blueprint(localized_settings)

	from app.settings.dev import dev_settings
	app.register_blueprint(dev_settings)

	from app.libraries import libraries
	app.register_blueprint(libraries)

	from app.lists import lists
	app.register_blueprint(lists)

	if app.config["SCHEDULERS_ENABLED"]:
		post_scheduler = threading.Thread(
			target=publish_posts
		)
		post_scheduler.start()

		twitter_scheduler = threading.Thread(
			target=publish_posts
		)
		twitter_scheduler.start()

	return app
