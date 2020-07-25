from flask import Blueprint

post = Blueprint('post_web', __name__)
from app.web.post import routes