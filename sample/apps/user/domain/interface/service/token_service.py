from abc import abstractmethod
from typing import Protocol, runtime_checkable

from sample.apps.user.domain.model.user import User


@runtime_checkable
class IAsyncTokenService(Protocol):
    @abstractmethod
    async def generate_token(self, user: User) -> str:
        ...
