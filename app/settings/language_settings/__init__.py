from flask import Blueprint
language_settings = Blueprint('language_settings', __name__, template_folder='templates')
from app.settings.language_settings import routes

