from flask import render_template
from . import error

@error.errorhandler(401)
def authentication_failed(error):
    return render_template('401.html'), 401

@error.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@error.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500
