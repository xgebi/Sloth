from flask import Blueprint

menu = Blueprint('menu', __name__, template_folder='templates')
from app.routes.settings.themes.menu import routes
