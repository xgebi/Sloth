from flask import request, flash, url_for, current_app, abort, redirect, render_template
import pytz

from app.utilities.db_connection import db_connection
from app.registration.registration import Registration

from app.web.registration import registration

@registration.route('/registration', methods=["GET", "POST"])
@db_connection
def registration_steps(*args, connection=None, **kwargs):	
	if (request.method.upper() == "GET"):
		return render_template("registration.html", registration={}, timezones=pytz.all_timezones)

	if connection is None:		
		return render_template("registration.html", registration={}, timezones=pytz.all_timezones, error=True), 500
	# registration
	user_data = request.form.to_dict()

	register = Registration(connection)
	result = register.initial_settings(filled=user_data)
	#success
	if (result.get("state") is not None and result.get("state") == "ok"):
		return redirect("/login")

	#failure
	error="Unknown error"
	status = result["status"] if result.get("status") else 500
	
	if (result.get("error") is not None):
		error = result["error"]
	return render_template("registration.html", registration={}, timezones=pytz.all_timezones, error=error), status
	