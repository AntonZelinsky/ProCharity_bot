import hashlib
from flask import request, jsonify, make_response
from functools import wraps

from app import config
from app.logger import webhooks_logger as logger

WEBHOOKS_TOKEN = hashlib.sha1(config.TOKEN_FOR_WEBHOOKS.encode('utf-8')).hexdigest()


def check_webhooks_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            webhooks_token = request.headers['token']
        except KeyError:
            logger.info('Request without token!')
            return make_response(jsonify(result='Access is denied'), 403)
        token = hashlib.sha1(webhooks_token.encode('utf-8')).hexdigest()
        if not token or token != WEBHOOKS_TOKEN:
            logger.info('Token is invalid!')
            return make_response(jsonify(result='Access is denied'), 403)
        return f(*args, **kwargs)
    return decorated
