from flask import Blueprint

dev_settings = Blueprint('dev_settings', __name__)

from app.settings.dev import routes
