from pydantic import BaseModel, Extra, NonNegativeInt


class RequestBase(BaseModel):
    """Базовый класс для моделей запросов.
    Запрещена передача полей не предусмотренных схемой."""
    id: NonNegativeInt

    class Config:
        extra = Extra.forbid
