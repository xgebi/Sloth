from flask import Blueprint

authn = Blueprint('authn', __name__)
from app.routes.v2.authn import routes