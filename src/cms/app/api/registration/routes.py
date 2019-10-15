from flask import render_template, request, flash, url_for, current_app, abort

import json
import os
import psycopg2
import uuid
from psycopg2 import sql, errors
import bcrypt
from pathlib import Path
import traceback

from app.utilities.db_connection import db_connection
from app.posts.posts_generator import PostsGenerator
from app.registration import Registration

from app.api.registration import registration

@registration.route("/api/register", methods=['POST'])
@db_connection
def initial_settings(*args, connection=None, **kwargs):
	register = Registration(connection)
	result = register.initial_settings(filled=json.loads(request.data))
	if result["error"]:
		return json.dumps({"error": result["error"]}), result["status"]
	return json.dumps({"status": result["state"]}), result["status"]
