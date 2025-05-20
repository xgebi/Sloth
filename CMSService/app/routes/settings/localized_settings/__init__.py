from flask import Blueprint

localized_settings = Blueprint('localized_settings', __name__)
from app.routes.settings.localized_settings import routes
