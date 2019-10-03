from flask import render_template, request, flash, url_for, current_app, abort

from pathlib import Path
import json
import os

import psycopg2
import uuid

from app.api.initialization import initialization

@initialization.route("/api/init")
def check_registration_lock():
	registration_lock_file = Path(os.path.join(os.getcwd(), 'registration.lock'))
	return json.dumps({ "initialized" : registration_lock_file.is_file()})
