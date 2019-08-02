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

	bcrypt.init_app(app)

	from app.entry import entry
	app.register_blueprint(entry)

	from app.errors import errors
	app.register_blueprint(errors)

	from app.api.initialization import initialization
	app.register_blueprint(initialization)

	from app.api.registration import registration
	app.register_blueprint(registration)

	from app.api.sloth_login import sloth_login
	app.register_blueprint(sloth_login)

	from app.api.dashboard import dashboard
	app.register_blueprint(dashboard)

	from app.api.sloth_settings import sloth_settings
	app.register_blueprint(sloth_settings)

	from app.api.posts.posts_list import posts_list
	app.register_blueprint(posts_list)

	from app.api.post import post
	app.register_blueprint(post)

	return app