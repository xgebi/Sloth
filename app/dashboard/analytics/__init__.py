from flask import Blueprint

analytics = Blueprint('analytics', __name__)
from app.dashboard.analytics import routes
