from flask import Blueprint
posts = Blueprint('posts', __name__, template_folder='templates')
from app.posts import routes