from sqlalchemy.orm import Session

from core.repositories.abstract_repository import AbstractRepository
from typing import Optional

from app.models import User


class UserRepository(AbstractRepository):

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_or_none(self, telegram_id: int) -> Optional[User]:
        return self.session.get(User, telegram_id)

    def get(self, telegram_id: int) -> User:
        user = self.get_or_none(telegram_id)
        if not user:
            raise LookupError(f'User ID={telegram_id} not found')
        return user

    def create(self, user: User) -> User:
        self.session.add(User)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update(self, user: User) -> None:
        pass
