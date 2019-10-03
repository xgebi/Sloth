from flask import request, redirect, url_for
import os
from pathlib import Path

from app import create_app

flask_app = create_app('dev')

@flask_app.before_request
def before_first_request():
	registration_lock_file = Path(os.path.join(os.getcwd(), 'registration.lock'))
	if not (request.path.startswith('/api') or request.path.startswith('/registration')  or request.path.startswith('/static')) and not registration_lock_file.is_file():
		return redirect('/registration')

with flask_app.app_context():
	flask_app.run()
