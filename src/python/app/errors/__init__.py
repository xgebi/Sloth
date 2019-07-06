from flask import Blueprint
errors = Blueprint('errors', __name__, template_folder='templates')
from app.errors import routes