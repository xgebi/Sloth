from flask import render_template, request, flash, url_for, current_app, abort

from app.web.registration import registration as reg

@reg.route('/registration')
def registration_step_1():
	return render_template("step-1.html")