from app.utilities.db_connection import db_connection_legacy

from app.webmentions import webmentions


@webmentions.route("/api/web-mentions", methods=["POST"])
@db_connection_legacy
def record_web_mentions(*args, **kwargs):
    pass
