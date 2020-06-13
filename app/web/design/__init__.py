from flask import Blueprint

design = Blueprint('design', __name__)
from app.web.design import routes
