from flask import Blueprint
registration = Blueprint('api_registration', __name__, template_folder='templates')
from app.api.registration import routes