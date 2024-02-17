from abc import ABC, abstractmethod
from uuid import UUID

from sample.apps.user.domain.model.user import User
from spakky.domain.interfaces.repository import IAsyncGenericRepository


class IAsyncUserRepository(IAsyncGenericRepository[User, UUID], ABC):
    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        ...
