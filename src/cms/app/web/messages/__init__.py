from flask import Blueprint
messages = Blueprint('messages', __name__)
from app.web.messages import routes