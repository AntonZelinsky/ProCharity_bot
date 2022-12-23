from typing import Optional
from pydantic import Field, NonNegativeInt, StrictStr, root_validator

from app.request_models.request_base import RequestBase


class CategoryCreateRequest(RequestBase):
    name: StrictStr = Field(min_length=2, max_length=100)
    parent_id: Optional[NonNegativeInt] = None

    @root_validator(skip_on_failure=True)
    def check_not_self_parent(cls, values):
        if values['parent_id'] and values['parent_id'] == values['id']:
            raise ValueError('Category cannot inherit from itself.')
        return values
