from flask import request, flash, url_for, current_app

from app.errors import errors

@errors.errorhandler(500)
def internal_error(error):
	pass
	#return render_toe('500.toe'), 500

@errors.errorhandler(404)
def not_found(error):
	return "404 error",404