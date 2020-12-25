from flask import current_app
from functools import wraps
import psycopg2


def db_connection(fn):
    @wraps(fn)
    def wrapper(*args, connection=None, **kwargs):
        if connection is not None:
            return fn(*args, connection=connection, **kwargs)

        config = current_app.config
        con = psycopg2.connect(dbname=config["DATABASE_NAME"], user=config["DATABASE_USER"],
                               host=config["DATABASE_URL"], port=config["DATABASE_PORT"],
                               password=config["DATABASE_PASSWORD"])
        return fn(*args, connection=con, **kwargs)
    return wrapper
