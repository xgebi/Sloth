import psycopg

from app.authorization.authorize import authorize_web
from app.utilities.db_connection import db_connection
from app.settings.integrations import integrations


@integrations.route("/settings/integrations", methods=["GET"])
@authorize_web(1)
@db_connection
def show_integrations_settings(*args, connection: psycopg.Connection, **kwargs):
    pass