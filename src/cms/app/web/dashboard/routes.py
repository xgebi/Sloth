from flask import request, flash, url_for, current_app, abort, redirect
from app.utilities.db_connection import db_connection

from toes.toes import render_toe

import bcrypt

from app.web.dashboard import dashboard

@dashboard.route('/dashboard')
def show_dashboard():
   return render_toe(template="dashboard.toe", path_to_templates=current_app.config["TEMPLATES_PATH"])