from flask import Blueprint

dashboard = Blueprint('dash', __name__)
from app.web.dashboard import routes
