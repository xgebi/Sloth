# app/__init__.py
import os
from flask import Flask
#from flask_login import LoginManager
from flask_bcrypt import Bcrypt

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

	from app.errors import errors
	app.register_blueprint(errors)

	from app.api.initialization import initialization
	app.register_blueprint(initialization)

	from app.api.registration import registration as api_registration
	app.register_blueprint(api_registration)

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

	from app.web.registration import registration as web_registration
	app.register_blueprint(web_registration)

	from app.web.login import login
	app.register_blueprint(login)

	from app.web.login import login
	app.register_blueprint(login)

	from app.web.dashboard import dashboard as dash
	app.register_blueprint(dash)

	from app.web.settings import settings as web_settings
	app.register_blueprint(web_settings)

	return app