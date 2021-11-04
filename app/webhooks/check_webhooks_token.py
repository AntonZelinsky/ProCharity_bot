from flask import request, jsonify, make_response
from functools import wraps

from app import config
from app.logger import webhooks_logger as logger


def check_webhooks_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not config.ACCESS_TOKEN_FOR_PROCHARITY:
            return f(*args, **kwargs)
        token = request.headers.get('token')
        if not token:
            logger.info('Request without token!')
            return make_response(jsonify(result='Access is denied'), 403)
        if token != config.ACCESS_TOKEN_FOR_PROCHARITY:
            logger.info('Token is invalid!')
            return make_response(jsonify(result='Access is denied'), 403)
        return f(*args, **kwargs)
    return decorated
