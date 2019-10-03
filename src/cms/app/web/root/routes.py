from flask import render_template, request, flash, url_for, current_app, abort

from app.web.root import root

@root.route("/")
def serve_root():
	print("He?")
	return render_template('root.html')
