from pydantic import parse_obj_as, ValidationError
from werkzeug.exceptions import BadRequest

from app.logger import webhooks_logger as logger


def request_to_context(context, request):
    if not request.json:
        logger.error(f'{context}: Json contains no data')
        raise BadRequest('Json contains no data')
    try:
        request_data = parse_obj_as(list[context], obj=request.json)
        return request_data
    except ValidationError as error:
        logger.error(f'{error}')
        raise BadRequest(error)
