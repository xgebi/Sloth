from flask import Blueprint
entry = Blueprint('entry', __name__, template_folder='templates')
from app.entry import routes