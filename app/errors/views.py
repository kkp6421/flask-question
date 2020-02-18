from flask import render_template
from . import error

@error.app_errorhandler(401)
def authentication_failed(error):
    return render_template('401.html'), 401

@error.app_errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@error.app_errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500
