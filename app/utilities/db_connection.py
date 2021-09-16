from typing import Optional
from flask import current_app, make_response
from functools import wraps
import psycopg2
import psycopg
import json


def db_connection_legacy(fn):
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


def db_connection(fn):
    """
    Decorator function which creates a connection to database for the function

    :param fn:
    :return:
    """
    @wraps(fn)
    def wrapper(*args, connection: Optional[psycopg.Connection] = None, **kwargs):
        if connection is not None:
            return fn(*args, connection=connection, **kwargs)

        config = current_app.config
        conn_str = f"postgresql://{config['DATABASE_USER']}:{config['DATABASE_PASSWORD']}@{config['DATABASE_URL']}:{config['DATABASE_PORT']}/{config['DATABASE_NAME']}"
        try:
            with psycopg.connect(conn_str) as conn:
                return fn(*args, connection=conn, **kwargs)
        except psycopg.errors.DatabaseError:
            return None

    return wrapper
