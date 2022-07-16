from flask import Blueprint

mock_endpoints = Blueprint('mock_endpoints', __name__)

from app.mock_endpoints import routes