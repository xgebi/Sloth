from flask import Blueprint

analytics = Blueprint('analytics', __name__)
from app.routes.dashboard.analytics import routes
