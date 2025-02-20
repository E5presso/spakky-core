from abc import abstractmethod
from typing import Awaitable, Callable, Protocol, TypeAlias, TypeVar, runtime_checkable

from spakky.domain.models.event import AbstractDomainEvent

DomainEventT = TypeVar("DomainEventT", bound=AbstractDomainEvent)
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


@runtime_checkable
class IAsyncEventConsumer(Protocol):
    @abstractmethod
    def register(
        self,
        event: type[DomainEventT],
        handler: IAsyncEventHandlerCallback[DomainEventT],
    ) -> None: ...
