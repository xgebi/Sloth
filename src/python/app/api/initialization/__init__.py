from flask import Blueprint
initialization = Blueprint('initialization', __name__, template_folder='templates')
from app.api.initialization import routes