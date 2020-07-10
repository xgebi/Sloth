from flask import Blueprint

media = Blueprint('media_web', __name__)
from app.web.media import routes