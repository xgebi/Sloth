from flask import request, current_app
from functools import wraps
import psycopg2

def db_connection(fn):
	@wraps(fn)
	def wrapper(*args, **kwargs):
		config = current_app.config
		con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")
		
		return fn(*args, connection=con, **kwargs)
	return wrapper