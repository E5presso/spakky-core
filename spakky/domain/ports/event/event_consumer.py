from typing import Protocol, runtime_checkable

from spakky.domain.models.event import DomainEvent


@runtime_checkable
class IEventConsumer(Protocol):
    def invoke(self, event: DomainEvent) -> None: ...


@runtime_checkable
class IAsyncEventConsumer(Protocol):
    async def invoke(self, event: DomainEvent) -> None: ...
