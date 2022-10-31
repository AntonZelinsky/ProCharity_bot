import abc
from typing import Optional, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

DatabaseModel = TypeVar("DatabaseModel")


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @abc.abstractmethod
    async def get_or_none(self, telegram_id: int) -> Optional[DatabaseModel]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, telegram_id: int) -> DatabaseModel:
        raise NotImplementedError

    @abc.abstractmethod
    async def create(self, instance: DatabaseModel) -> DatabaseModel:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, instance: DatabaseModel) -> DatabaseModel:
        raise NotImplementedError
