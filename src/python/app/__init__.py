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

    from app.wizard import wizard
    app.register_blueprint(wizard)

    from app.authentication import authentication
    app.register_blueprint(authentication)

    from app.administration import administration
    app.register_blueprint(administration)

    from app.administration.dashboard import dashboard
    app.register_blueprint(dashboard)

    from app.administration.settings import settings
    app.register_blueprint(settings)

    return app