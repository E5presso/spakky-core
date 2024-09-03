from abc import abstractmethod
from typing import TypeVar, Callable, Protocol, Awaitable, TypeAlias, runtime_checkable
from asyncio import Event as AsyncEvent
from threading import Event as ThreadEvent

from spakky.domain.models.event import DomainEvent

DomainEventT = TypeVar("DomainEventT", bound=DomainEvent)
IEventHandlerCallback: TypeAlias = Callable[[DomainEventT], None]
IAsyncEventHandlerCallback: TypeAlias = Callable[[DomainEventT], Awaitable[None]]


@runtime_checkable
class IEventConsumer(Protocol):
    @abstractmethod
    def register(
        self,
        event: type[DomainEventT],
        handler: IEventHandlerCallback[DomainEventT],
    ) -> None: ...

    @abstractmethod
    def start(self, cancellation_token: ThreadEvent) -> None: ...


@runtime_checkable
class IAsyncEventConsumer(Protocol):
    @abstractmethod
    def register(
        self,
        event: type[DomainEventT],
        handler: IAsyncEventHandlerCallback[DomainEventT],
    ) -> None: ...

    @abstractmethod
    async def start(self, cancellation_token: AsyncEvent) -> None: ...
