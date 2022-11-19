from flask import Blueprint
settings_users = Blueprint('settings_users', __name__)

from app.settings.users import routes