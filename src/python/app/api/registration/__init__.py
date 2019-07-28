from flask import Blueprint
registration = Blueprint('registration', __name__, template_folder='templates')
from app.api.registration import routes