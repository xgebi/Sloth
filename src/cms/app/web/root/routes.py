from flask import request, flash, url_for, current_app, abort

from toes.toes import render_toe

from app.web.root import root

@root.route("/")
def serve_root():
	print("He?")
	return render_toe('root.html')
