from flask import Blueprint
post_types = Blueprint('post_types', __name__, template_folder = 'templates')
from app.api.posts.post_types import routes