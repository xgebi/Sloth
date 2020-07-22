from flask import Blueprint
integrations = Blueprint('integrations', __name__, template_folder = 'templates')
from app.integrations import integrations