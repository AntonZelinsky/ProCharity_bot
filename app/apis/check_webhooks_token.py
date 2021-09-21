import hashlib
from flask import request, jsonify, make_response
from functools import wraps

from app import config
from app.logger import webhooks_logger as logger


def check_webhooks_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            request.headers['token']
        except KeyError:
            logger.info('Request without token!')
            return make_response(jsonify(result='Access is denied'), 403)
        token = request.headers['token']
        if not config.TOKEN_FOR_WEBHOOKS:
            return f(*args, **kwargs)
        if not token or token != config.TOKEN_FOR_WEBHOOKS:
            logger.info('Token is invalid!')
            return make_response(jsonify(result='Access is denied'), 403)
        return f(*args, **kwargs)
    return decorated
