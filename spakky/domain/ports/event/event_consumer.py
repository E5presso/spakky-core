from abc import abstractmethod
from typing import (
    Any,
    TypeVar,
    Callable,
    Protocol,
    Awaitable,
    TypeAlias,
    runtime_checkable,
)

from spakky.domain.models.event import DomainEvent
from spakky.task.cancellation_token import ICancellationToken

DomainEventT = TypeVar("DomainEventT", bound=DomainEvent)
IEventHandlerCallback: TypeAlias = Callable[[Any, DomainEventT], None]
IAsyncEventHandlerCallback: TypeAlias = Callable[[Any, DomainEventT], Awaitable[None]]


@runtime_checkable
class IEventConsumer(Protocol):
    @abstractmethod
    def register(
        self,
        event: type[DomainEventT],
        handler: IEventHandlerCallback[DomainEventT],
    ) -> None: ...

    @abstractmethod
    def start(self, cancellation_token: ICancellationToken) -> None: ...


@runtime_checkable
class IAsyncEventConsumer(Protocol):
    @abstractmethod
    async def register(
        self,
        event: type[DomainEventT],
        handler: IAsyncEventHandlerCallback[DomainEventT],
    ) -> None: ...

    @abstractmethod
    async def start(self, cancellation_token: ICancellationToken) -> None: ...
