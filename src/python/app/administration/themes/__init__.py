from flask import Blueprint
themes = Blueprint('themes', __name__, template_folder='templates')
from app.administration.themes import routes