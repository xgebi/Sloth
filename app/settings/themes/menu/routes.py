from flask import flash, render_template
import re

from app.authorization.authorize import authorize_web
import datetime

from app.utilities.db_connection import db_connection

from app.settings.themes.menu import menu


@menu.route("/settings/themes/menu")
@authorize_web(0)
@db_connection
def show_menus(*args, permission_level, connection, **kwargs):
    return render_template("menu.html", permission_level=permission_level)
