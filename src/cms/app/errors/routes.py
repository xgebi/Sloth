from flask import request, flash, url_for, current_app

from toes.toes import render_toe

from app.errors import errors

@errors.errorhandler(500)
def internal_error(error):

	return render_toe('500.toe'), 500

@errors.errorhandler(404)
def not_found(error):
	return "404 error",404