from flask import request, flash, url_for, current_app, abort, redirect

from toes.toes import render_toe

from app.web.settings import settings

@settings.route("/settings")
# do something about security!!!
def show_settings():
	settings = {}
	return render_toe(template="settings.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data=settings)
