from typing import Optional
from pydantic import Field, NonNegativeInt, StrictStr, root_validator

from app.request_models.request_base import RequestBase


class CategoryCreateRequest(RequestBase):
    id: NonNegativeInt
    name: StrictStr = Field(min_length=2, max_length=100)
    parent_id: Optional[NonNegativeInt]

    @root_validator
    def check_not_self_parent(cls, values):
        if values['id'] == values['parent_id']:
            raise ValueError('category cannot inherit from itself')
        return values
