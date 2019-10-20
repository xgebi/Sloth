from flask import render_template, request, flash, url_for, current_app, abort, redirect
from app.utilities.db_connection import db_connection

import bcrypt

from app.web.dashboard import dashboard

@dashboard.route('/dashboard')
def show_dashboard():
   return render_template('dashboard.html')