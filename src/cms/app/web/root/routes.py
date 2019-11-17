from flask import request, flash, url_for, current_app, abort, redirect

from app.web.root import root

@root.route("/")
def serve_root():
	return redirect("/dashboard")
