from flask import Blueprint
settings_users = Blueprint('settings_users', __name__)

from app.routes.settings.users import routes