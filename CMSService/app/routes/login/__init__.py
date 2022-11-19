from flask import Blueprint

login = Blueprint('login', __name__)
from app.routes.login import routes
