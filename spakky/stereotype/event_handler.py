from typing import Any, Generic, TypeVar, Callable, Awaitable, TypeAlias
from dataclasses import dataclass

from spakky.bean.bean import Bean
from spakky.core.annotation import FunctionAnnotation
from spakky.domain.models.domain_event import DomainEvent

EventT = TypeVar("EventT", bound=DomainEvent)
IEventHandlerFunction: TypeAlias = Callable[[Any, EventT], Awaitable[None]]


@dataclass
class Event(FunctionAnnotation, Generic[EventT]):
    event: type[EventT]

    def __call__(
        self, obj: IEventHandlerFunction[EventT]
    ) -> IEventHandlerFunction[EventT]:
        return super().__call__(obj)


def event(
    event_type: type[EventT],
) -> Callable[[IEventHandlerFunction[EventT]], IEventHandlerFunction[EventT]]:
    def wrapper(method: IEventHandlerFunction[EventT]) -> IEventHandlerFunction[EventT]:
        return Event[EventT](event_type)(method)

    return wrapper


@dataclass
class EventHandler(Bean):
    ...
