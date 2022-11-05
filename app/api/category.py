from typing import Optional
from pydantic import Field, NonNegativeInt, StrictStr
from flask_pydantic import validate

from .request_base import RequestBase


class CategoryCreateRequest(RequestBase):
    id: NonNegativeInt
    name: StrictStr = Field(min_length=2, max_length=100)
    parent_id: Optional[NonNegativeInt]

    @validate('parent_id')
    def check_not_self_parent(cls, v, values):
        if v and 'id' in values and v == values['id']:
            raise ValueError('category cannot inherit from itself')
        return v
