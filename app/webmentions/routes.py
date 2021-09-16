from app.utilities.db_connection import db_connection_legacy

from app.webmentions import webmentions


@webmentions.route("/api/webmentions", methods=["POST"])
@db_connection_legacy
def record_webmention(*args, **kwargs):
    pass
