from flask import Blueprint
registration = Blueprint('web_registration', __name__)
from app.web.registration import routes