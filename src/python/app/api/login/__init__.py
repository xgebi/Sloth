from flask import Blueprint
login = Blueprint('login', __name__, template_folder='templates')
from app.api.login import routes