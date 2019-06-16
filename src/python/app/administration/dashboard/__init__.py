from flask import Blueprint
dashboard = Blueprint('dashboard', __name__, template_folder='templates')
from app.administration.dashboard import routes