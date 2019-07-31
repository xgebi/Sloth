from flask import Blueprint
sloth_settings = Blueprint('sloth_settings', __name__, template_folder='templates')
from app.api.sloth_settings import routes