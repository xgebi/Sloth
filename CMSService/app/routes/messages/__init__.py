from flask import Blueprint

messages = Blueprint('messages', __name__)
from app.routes.messages import routes