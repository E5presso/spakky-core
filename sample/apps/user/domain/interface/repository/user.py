from abc import ABC
from uuid import UUID

from sample.apps.user.domain.model.user import User
from spakky.domain.interfaces.repository import IAsyncGenericRepository


class IAsyncUserRepository(IAsyncGenericRepository[User, UUID], ABC):
    ...
