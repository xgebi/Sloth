from flask import Blueprint
login = Blueprint('login', __name__)
from app.web.login import routes