from flask import Blueprint

media = Blueprint('media_api', __name__, template_folder='templates')
from app.media import routes
