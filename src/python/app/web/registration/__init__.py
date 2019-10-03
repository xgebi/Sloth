from flask import Blueprint
registration = Blueprint('web_registration', __name__, template_folder='templates')
from app.web.registration import routes