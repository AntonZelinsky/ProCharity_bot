from typing import Optional
from pydantic import Field, NonNegativeInt, StrictStr
from flask_pydantic import validate

from app.request_models.request_base import RequestBase


class CategoryCreateRequest(RequestBase):
    id: NonNegativeInt
    name: StrictStr = Field(min_length=2, max_length=100)
    parent_id: Optional[NonNegativeInt]

    @validate('parent_id')
    def check_not_self_parent(cls, parent_id, values):
        if parent_id and 'id' in values and parent_id == values['id']:
            raise ValueError('category cannot inherit from itself')
        return parent_id
