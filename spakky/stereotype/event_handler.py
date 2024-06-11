from typing import Any, Callable, Protocol, Awaitable, runtime_checkable
from dataclasses import dataclass

from spakky.bean.bean import Bean
from spakky.core.annotation import FunctionAnnotation
from spakky.domain.models.domain_event import DomainEvent


@runtime_checkable
class IEventHandlerCallaback(Protocol):
    # pylint: disable=no-self-argument
    def __call__(
        self_,  # type: ignore
        self: Any,
        event: DomainEvent,
    ) -> Awaitable[None]: ...


@dataclass
class EventRoute(FunctionAnnotation):
    event_type: type[DomainEvent]

    def __call__(self, obj: IEventHandlerCallaback) -> IEventHandlerCallaback:
        return super().__call__(obj)


def on_event(
    event_type: type[DomainEvent],
) -> Callable[[IEventHandlerCallaback], IEventHandlerCallaback]:
    def wrapper(method: IEventHandlerCallaback) -> IEventHandlerCallaback:
        return EventRoute(event_type)(method)

    return wrapper


@dataclass
class EventHandler(Bean): ...
