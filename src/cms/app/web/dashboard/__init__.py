from flask import Blueprint
dashboard = Blueprint('dash', __name__, template_folder='templates')
from app.web.dashboard import routes