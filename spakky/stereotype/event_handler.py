from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Generic, TypeAlias, TypeVar

from spakky.core.annotation import FunctionAnnotation
from spakky.domain.models.event import AbstractDomainEvent
from spakky.pod.annotations.pod import Pod

DomainEventT = TypeVar("DomainEventT", bound=AbstractDomainEvent)
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
) -> Callable[
    [IEventHandlerCallback[DomainEventT]], IEventHandlerCallback[DomainEventT]
]:
    def wrapper(
        method: IEventHandlerCallback[DomainEventT],
    ) -> IEventHandlerCallback[DomainEventT]:
        return EventRoute(event_type)(method)

    return wrapper


@dataclass(eq=False)
class EventHandler(Pod): ...
