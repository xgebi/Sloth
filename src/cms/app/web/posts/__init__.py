from flask import Blueprint
posts = Blueprint('posts_web', __name__)
from app.web.posts import routes