from flask import request, redirect
import os
from pathlib import Path

from app import create_app

flask_app = create_app('dev')

#@flask_app.before_first_request
@flask_app.before_request
def before_first_request():
	print(request.path)
	if not request.path.startswith('/api') and not registration_lock_file.is_file():
		return redirect('/register')

with flask_app.app_context():
	flask_app.run()
