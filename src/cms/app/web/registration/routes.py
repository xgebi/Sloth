from flask import request, flash, url_for, current_app, abort, redirect, render_template
from app.utilities.db_connection import db_connection
from app.registration.registration import Registration

from app.web.registration import registration

@registration.route('/registration', methods=["GET", "POST"])
@db_connection
def registration_steps(*args, connection=None, **kwargs):	
	if (request.method.upper() == "GET"):
		return render_template(template="step-1.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data={ "page_title": "SlothCMS registration | Step 1"})

	if connection is None:
		print("heee");
		return render_template(template="step-1.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data={ "error":"Error connecting to database", "page_title": "SlothCMS registration | Step 1"}), 500
	# registration
	user_data = request.form.to_dict()

	# TODO check pass code
	if current_app.config["PASSCODE"] != user_data["passcode"]:
		print("haaa");
		import pdb; pdb.set_trace()
		return render_template(template="step-1.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data={ "error":"Not authorized to register", "page_title": "SlothCMS registration | Step 1"}), 500

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
	return render_template(template="step-1.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data={ "filled": user_data, "error":error, "page_title": "SlothCMS registration | Step 1"}), status

@registration.route('/registration/done', methods=["GET"])
def registration_done(*args, **kwargs):
	return render_template(template="step-2.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data={ "page_title": "SlothCMS registration done "})
	