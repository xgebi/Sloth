from flask import Blueprint

messages = Blueprint('messages_api', __name__, template_folder='templates')
from app.api.messages import routes