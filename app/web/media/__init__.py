from flask import Blueprint

media = Blueprint('media', __name__)
from app.web.media import routes