from flask import Blueprint

libraries = Blueprint('libraries', __name__)
from app.libraries import routes