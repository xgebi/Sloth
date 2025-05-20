from flask import Blueprint
settings_themes = Blueprint('web_settings_themes', __name__)

from app.routes.settings.themes import routes
