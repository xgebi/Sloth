from flask import render_template, request, flash, url_for, current_app, abort
from app.utilities.db_connection import db_connection
from app.registration import Registration

from app.web.registration import registration

@registration.route('/registration', methods=["GET", "POST"])
@db_connection
def registration_steps(*args, connection=None, **kwargs):
	if (request.method.upper() == "GET"):
		return render_template("step-1.html")

	if connection is None:
		return render_template("step-1.html", errors="database")
	# registration
	register = Registration(connection)
	result = register.initial_settings()
	#success
	return render_template("step-2.html")

	#failure
	return render_template("step-1.html", data=user_data, error="general")
	