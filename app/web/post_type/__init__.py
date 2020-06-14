from flask import Blueprint

post_type = Blueprint('post_type', __name__)
from app.web.post_type import routes
