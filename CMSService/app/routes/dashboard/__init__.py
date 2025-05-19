from flask import Blueprint

dashboard = Blueprint('dash', __name__)
from app.routes.dashboard import routes
