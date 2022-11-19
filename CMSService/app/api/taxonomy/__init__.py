from flask import Blueprint

taxonomy = Blueprint('taxonomy_api', __name__, template_folder='templates')
from app.api.taxonomy import routes
