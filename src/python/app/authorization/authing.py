from flask import render_template, request, flash, redirect, url_for, current_app, abort
from functools import wraps
import json

from app.authorization.user import User

def authing(permission_level):
	def inner(fn):
		@wraps(fn)
		def wrapper(*args, **kwargs):
			auth = request.headers.get('authorization').split(":")
			user = User(auth[0], auth[1])
			if (user.authorize_user(permission_level)):
				return fn(*args, **kwargs)
			return json.dumps({ "dashboard": "Error" }), 403
		return wrapper
	return inner