from flask import Blueprint
root = Blueprint('root', __name__)
from app.web.root import routes