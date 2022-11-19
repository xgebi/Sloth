from flask import redirect

from app.root import root


@root.route("/")
def serve_root():
	return redirect("/dashboard")
