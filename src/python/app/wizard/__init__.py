from flask import Blueprint
wizard = Blueprint('wizard', __name__, template_folder='templates')
from app.wizard import routes