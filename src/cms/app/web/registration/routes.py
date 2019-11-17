from flask import request, flash, url_for, current_app, abort, redirect
from app.utilities.db_connection import db_connection
from app.registration import Registration
from toes.toes import render_toe

from app.web.registration import registration

@registration.route('/registration', methods=["GET", "POST"])
@db_connection
def registration_steps(*args, connection=None, **kwargs):	
	import pdb; pdb.set_trace()
	if (request.method.upper() == "GET"):
		return render_toe(template="step-1.toe", path_to_templates=current_app.config["TEMPLATES_PATH"])

	if connection is None:
		return render_toe(template="step-1.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data={ "error":"Error connecting to database"}), 500
	# registration
	user_data = request.form.to_dict()
	register = Registration(connection)
	result = register.initial_settings(filled=user_data)
	#success
	if (result.get("state") is not None and result.get("state") == "ok"):
		return redirect("/registration/done")

	#failure
	error="Unknown error"
	status = result["status"] if result.get("status") else 500
	
	if (result.get("error") is not None):
		error = result["error"]
	return render_toe(template="step-1.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data={ "filled": user_data, "error":error}), status

@registration.route('/registration/done', methods=["GET"])
def registration_done(*args, **kwargs):
	import pdb; pdb.set_trace()
	return render_toe(template="step-2.toe", path_to_templates=current_app.config["TEMPLATES_PATH"])
	