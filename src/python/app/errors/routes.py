from flask import render_template, request, flash, redirect, url_for, current_app

from app.errors import errors

@app.errorhandler(500)
def internal_error(error):

	return render_template('500.html'), 500

@app.errorhandler(404)
def not_found(error):
	return "404 error",404