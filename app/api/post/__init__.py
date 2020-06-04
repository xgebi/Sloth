from flask import Blueprint
post = Blueprint('post_api', __name__, template_folder='templates')
from app.api.post import routes