from sqlalchemy.ext.asyncio import AsyncSession

from core.repositories.abstract_repository import AbstractRepository, DatabaseModel
from typing import Optional

from app.models import User


class UserRepository(AbstractRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def get_or_none(self, telegram_id: int) -> Optional[User]:
        return self.session.get(User, telegram_id)

    async def get(self, telegram_id: int) -> User:
        user = await self.get_or_none(telegram_id)
        if not user:
            raise LookupError(f'User ID={telegram_id} not found')
        return user

    async def create(self, user: User) -> User:
        self.session.add(User)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User) -> None:
        pass
