from flask import Blueprint

webmentions = Blueprint('webmentions', __name__)

from app.webmentions import routes