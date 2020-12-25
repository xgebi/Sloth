from flask import Blueprint
rss = Blueprint('rss', __name__)
from app.rss import routes