from flask import current_app, make_response
from functools import wraps
import psycopg2
import json

def db_connection(fn):
    @wraps(fn)
    def wrapper(*args, connection=None, **kwargs):
        if connection is not None:
            return fn(*args, connection=connection, **kwargs)

        config = current_app.config
        try:
            con = psycopg2.connect(dbname=config["DATABASE_NAME"], user=config["DATABASE_USER"],
                                   host=config["DATABASE_URL"], port=config["DATABASE_PORT"],
                                   password=config["DATABASE_PASSWORD"])
        except Exception as e:
            response = make_response(json.dumps({"database_connection": "not working"}))
            response.headers['Content-Type'] = 'application/json'
            code = 500

            return response, code
        return fn(*args, connection=con, **kwargs)
    return wrapper
