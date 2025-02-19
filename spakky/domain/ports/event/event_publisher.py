from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.domain.models.event import AbstractDomainEvent


@runtime_checkable
class IEventPublisher(Protocol):
    @abstractmethod
    def publish(self, event: AbstractDomainEvent) -> None: ...


@runtime_checkable
class IAsyncEventPublisher(Protocol):
    @abstractmethod
    async def publish(self, event: AbstractDomainEvent) -> None: ...
