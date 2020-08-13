# app/__init__.py
from flask import Flask, request, redirect
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import os
from pathlib import Path

bcrypt = Bcrypt()


def create_app():  # dev, test, or prod

    app = Flask(__name__)
    cors = CORS(app)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )
    configuration = os.path.join(os.getcwd(), 'config', f'{os.environ["FLASK_ENV"]}.py')

    app.config.from_pyfile(configuration)
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

    from app.errors import errors
    app.register_blueprint(errors)

    from app.api.dashboard import dashboard
    app.register_blueprint(dashboard)

    from app.api.content_management import content_management
    app.register_blueprint(content_management)

    from app.web.root import root
    app.register_blueprint(root)

    from app.registration import registration
    app.register_blueprint(registration)

    from app.web.login import login
    app.register_blueprint(login)

    from app.web.dashboard import dashboard as dash
    app.register_blueprint(dash)

    from app.web.settings import settings as web_settings
    app.register_blueprint(web_settings)

    from app.settings.themes import settings_themes
    app.register_blueprint(settings_themes)

    from app.settings.themes.menu import menu
    app.register_blueprint(menu)

    from app.web.settings.content import content
    app.register_blueprint(content)

    from app.web.settings.users import settings_users
    app.register_blueprint(settings_users)

    from app.post import post
    app.register_blueprint(post)

    from app.web.design import design
    app.register_blueprint(design)

    from app.web.messages import messages
    app.register_blueprint(messages)

    from app.api.site import site
    app.register_blueprint(site)

    from app.web.post_type import post_type
    app.register_blueprint(post_type)

    from app.api.messages import messages as messages_api
    app.register_blueprint(messages_api)

    from app.api.taxonomy import taxonomy as taxonomy_api
    app.register_blueprint(taxonomy_api)

    from app.api.media import media as media_api
    app.register_blueprint(media_api)

    from app.web.media import media as media_web
    app.register_blueprint(media_web)

    return app
