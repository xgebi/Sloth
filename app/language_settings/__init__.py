from flask import Blueprint
language_settings = Blueprint('language_settings', __name__, template_folder = 'templates')
from app.language_settings import language_settings
