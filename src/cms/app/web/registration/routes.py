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
		return render_template("step-1.html", errors="Error connecting to database"), 500
	# registration
	user_data = request.form.to_dict()
	register = Registration(connection)
	result = register.initial_settings(filled=user_data)
	#success
	if (result.get("state") is not None and result.get("state") == "ok"):
		return render_template("step-2.html"), result["status"]

	#failure
	error="Unknown error"
	status = result["status"] if result.get("status") else 500
	
	if (result.get("error") is not None):
		error = result["error"]
	return render_template("step-1.html", data=user_data, error=error), status
	