from flask import Blueprint
root = Blueprint('root', __name__)
from app.root import routes