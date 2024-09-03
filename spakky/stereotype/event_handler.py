from typing import (
    Any,
    Generic,
    TypeVar,
    Callable,
    Protocol,
    Awaitable,
    TypeAlias,
    runtime_checkable,
)
from dataclasses import dataclass

from spakky.core.annotation import FunctionAnnotation
from spakky.domain.models.event import DomainEvent
from spakky.pod.pod import Pod

DomainEventT = TypeVar("DomainEventT", bound=DomainEvent)
IEventHandlerCallback: TypeAlias = Callable[[Any, DomainEventT], None | Awaitable[None]]


@dataclass
class EventRoute(FunctionAnnotation, Generic[DomainEventT]):
    event_type: type[DomainEventT]

    def __call__(
        self, obj: IEventHandlerCallback[DomainEventT]
    ) -> IEventHandlerCallback[DomainEventT]:
        return super().__call__(obj)


def on_event(
    event_type: type[DomainEventT],
) -> Callable[[IEventHandlerCallback[DomainEventT]], IEventHandlerCallback[DomainEventT]]:
    def wrapper(
        method: IEventHandlerCallback[DomainEventT],
    ) -> IEventHandlerCallback[DomainEventT]:
        return EventRoute(event_type)(method)

    return wrapper


@dataclass
class EventHandler(Pod): ...


@runtime_checkable
class IEventHandler(Protocol):
    def invoke(self, event: DomainEvent) -> None: ...


@runtime_checkable
class IAsyncEventHandler(Protocol):
    async def invoke(self, event: DomainEvent) -> None: ...
