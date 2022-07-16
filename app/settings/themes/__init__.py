from flask import Blueprint
settings_themes = Blueprint('web_settings_themes', __name__)

from app.settings.themes import routes
