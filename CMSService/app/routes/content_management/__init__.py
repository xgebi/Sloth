from flask import Blueprint
content_management = Blueprint('content_management_rest', __name__, template_folder='templates')
from app.routes.content_management import routes