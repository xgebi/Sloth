from flask import Blueprint
sloth_login = Blueprint('sloth_login', __name__, template_folder='templates')
from app.api.sloth_login import routes