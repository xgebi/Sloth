from flask import Blueprint
content = Blueprint('content', __name__, template_folder='templates')

from app.settings.content import routes
