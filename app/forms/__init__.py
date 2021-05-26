from flask import Blueprint

forms = Blueprint('forms', __name__)
from app.forms import routes