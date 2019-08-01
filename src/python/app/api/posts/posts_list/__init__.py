from flask import Blueprint
posts_list = Blueprint('posts_list', __name__, template_folder='templates')
from app.api.posts.posts_list import routes