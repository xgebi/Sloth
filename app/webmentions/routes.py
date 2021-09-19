from app.utilities.db_connection import db_connection

from app.webmentions import webmentions


@webmentions.route("/api/web-mentions", methods=["POST"])
@db_connection
def record_web_mentions(*args, **kwargs):
    pass
