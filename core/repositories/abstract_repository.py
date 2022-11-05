import abc
from typing import Optional, TypeVar

from sqlalchemy.orm import Session

DatabaseModel = TypeVar("DatabaseModel")


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def __init__(self, session: Session) -> None:
        self.session = session

    @abc.abstractmethod
    def get_or_none(self, telegram_id: int) -> Optional[DatabaseModel]:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, telegram_id: int) -> DatabaseModel:
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, instance: DatabaseModel) -> DatabaseModel:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, instance: DatabaseModel) -> DatabaseModel:
        raise NotImplementedError
