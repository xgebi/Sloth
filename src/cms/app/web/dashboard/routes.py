from flask import request, flash, url_for, current_app, abort, redirect
from app.utilities.db_connection import db_connection
from app.toes.toes import render_toe

import bcrypt

from app.web.dashboard import dashboard

@dashboard.route('/dashboard')
def show_dashboard():
   return render_toe('dashboard.html')