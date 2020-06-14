from flask import Blueprint

settings = Blueprint('web_settings', __name__)
from app.web.settings import routes
