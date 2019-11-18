from flask import request, redirect
from functools import wraps
import json

from app.authorization.user import User

def authorize_rest(permission_level):
	def inner(fn):
		@wraps(fn)
		def wrapper(*args, **kwargs):
			auth = request.headers.get('authorization').split(":")
			user = User(auth[0], auth[1])
			if (user.authorize_user(permission_level)):
				return fn(*args, **kwargs)
			return json.dumps({ "Unauthorized": True }), 403
		return wrapper
	return inner

def authorize_web(permission_level):
	def inner(fn):
		@wraps(fn)
		def wrapper(*args, **kwargs):
			auth = request.cookies.get('sloth_session')
			if auth is None:
				return redirect("/login")
			auth = auth.split(":")
			if len(auth) != 3:
				return redirect("/login")
			user = User(auth[1], auth[2])
			if (user.authorize_user(permission_level)):
				user.refresh_login()
				return fn(*args, **kwargs)
			return redirect("/login")
		return wrapper
	return inner