from flask import redirect

from app.root import root

# Route audited
@root.route("/")
def serve_root():
	return redirect("/dashboard")
