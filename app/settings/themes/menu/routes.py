from flask import flash, render_template
import re

from app.authorization.authorize import authorize_web
import datetime

from app.utilities.db_connection import db_connection

from settings.themes.menu import menu

@menu.route("/settings/themes/menu")
@authorize_web(0)
@db_connection
def show_menus(*args, connection, **kwargs):
    return render_template("menu.html")
