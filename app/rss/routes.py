from flask import redirect

from app.rss import rss


@rss.route("/rss")
def serve_rss():
    return "Hello"
