from app.utilities.db_connection import db_connection

from app.webmentions import webmentions


@webmentions.route("/api/webmentions", methods=["POST"])
@db_connection
def record_webmention(*args, **kwargs):
    pass
