# app/__init__.py
import os
from flask import Flask, request, redirect, url_for
#from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os
from pathlib import Path

#login_manager = LoginManager()
#login_manager.login_view = 'authentication.do_the_login'
#login_manager.session_protection = 'strong'
bcrypt = Bcrypt()


def create_app(config_type):  # dev, test, or prod

	app = Flask(__name__)
	configuration = os.path.join(os.getcwd(), 'config', config_type + '.py')
	
	app.config.from_pyfile(configuration)
	app.config["THEMES_PATH"] = os.path.join(os.getcwd(), 'themes')
	app.config["TEMPLATES_PATH"] = os.path.join(os.getcwd(), 'src', 'cms', 'app', 'templates')

	bcrypt.init_app(app)

	@app.before_request
	def before_first_request():
		registration_lock_file = Path(os.path.join(os.getcwd(), 'registration.lock'))
		if not (request.path.startswith('/api') or request.path.startswith('/registration') or request.path.startswith('/design')  or request.path.startswith('/static')) and not registration_lock_file.is_file():
			return redirect('/registration')

	from app.errors import errors
	app.register_blueprint(errors)

	from app.api.initialization import initialization
	app.register_blueprint(initialization)

	from app.api.sloth_login import sloth_login
	app.register_blueprint(sloth_login)

	from app.api.dashboard import dashboard
	app.register_blueprint(dashboard)

	from app.api.sloth_settings import sloth_settings
	app.register_blueprint(sloth_settings)

	from app.api.post import post
	app.register_blueprint(post)

	from app.api.posts.posts_list import posts_list
	app.register_blueprint(posts_list)

	from app.api.posts.post_categories import post_categories
	app.register_blueprint(post_categories)

	from app.api.posts.post_types import post_types
	app.register_blueprint(post_types)

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

	from app.web.login import login
	app.register_blueprint(login)

	from app.web.dashboard import dashboard as dash
	app.register_blueprint(dash)

	from app.web.settings import settings as web_settings
	app.register_blueprint(web_settings)

	from app.web.settings.themes import settings_themes as web_settings_themes
	app.register_blueprint(web_settings_themes)

	from app.web.posts import posts as web_posts
	app.register_blueprint(web_posts)

	from app.web.design import design
	app.register_blueprint(design)

	return app