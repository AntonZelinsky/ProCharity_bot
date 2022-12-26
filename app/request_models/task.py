from datetime import datetime, date
from typing import Optional
from pydantic import Extra, Field, HttpUrl, NonNegativeInt, StrictStr, validator

from app.request_models.request_base import RequestBase


class TaskCreateRequest(RequestBase):
    title: StrictStr = Field(min_length=2, max_length=256)
    name_organization: StrictStr = Field(min_length=2, max_length=100)
    deadline: date
    category_id: NonNegativeInt
    bonus: NonNegativeInt = 5
    location: Optional[StrictStr] = Field(max_length=100)
    link: HttpUrl
    description: Optional[StrictStr] = None

    class Config:
        extra = Extra.ignore

    @validator('deadline', pre=True)
    def validate_deadline(cls, deadline):
        return datetime.strptime(deadline, '%d.%m.%Y')
