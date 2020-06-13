from flask import Blueprint

post = Blueprint('post', __name__)
from app.web.post import routes