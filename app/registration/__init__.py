from flask import Blueprint
registration = Blueprint('web_registration', __name__)
from app.registration import routes