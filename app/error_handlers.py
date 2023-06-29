class InvalidAPIUsage(Exception):
    """
    Special class for custom Exceptions raised where it is necessary.
    If Exception is not explicitly defined raises HTTP 400 Bad Request.
    Error Message is required to clarify erroneous program behavior.
    """
    status_code = 400

    def __init__(self, message, status_code=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code


def invalid_api_usage(error):
    """
    InvalidAPIUsage handler function.
    """
    return error.message, error.status_code
