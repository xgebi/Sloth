from flask import Blueprint

dashboard = Blueprint('dash', __name__)
from app.dashboard import routes
