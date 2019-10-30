import json
from brighthive_authlib import OAuth2ProviderError
from data_resource_api.logging import LogFactory
from flask import jsonify
from werkzeug.exceptions import NotFound


class ApiError(Exception):
    def __init__(self, message, status_code=400):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

    def get_message(self):
        resp = {}
        resp['error'] = self.message
        return jsonify(resp)

    def get_status_code(self):
        return self.status_code


class ApiErrorLog(ApiError):
    pass


class MethodNotAllowed(ApiError):
    def __init__(self):
        message = "Method not allowed"
        status_code = 405
        ApiError.__init__(self, message, status_code)


def handle_errors(e):
    """Flask App Error Handler

    A generic error handler for Flask applications.

    Note:
        This error handler is essentially to ensure that OAuth 2.0 authorization errors
        are handled in an appropriate fashion. The application configuration used when
        building the application must set the PROPOGATE_EXPECTIONS environment variable to
        True in order for the exception to be propogated.

    Return:
        dict, int: The error message and associated error code.

    """
    if isinstance(e, OAuth2ProviderError):
        return json.dumps({'message': 'Access Denied'}), 401

    if isinstance(e, NotFound):
        return json.dumps({'error': 'Location not found'}), 404
    
    if isinstance(e, ApiError):
        return e.get_message(), e.get_status_code()

    logger = LogFactory.get_console_logger('data-model-manager')
    logger.exception("Encountered an error while processing a request.")

    if isinstance(e, ApiErrorLog):
        return e.get_message(), e.get_status_code()

    return e.get_response()
