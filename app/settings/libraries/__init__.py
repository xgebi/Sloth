from flask import Blueprint

libraries = Blueprint('libraries', __name__)
from app.settings.libraries import routes