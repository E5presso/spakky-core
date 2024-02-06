from abc import ABC
from copy import deepcopy
from typing import Generic, TypeVar, Sequence
from dataclasses import field

from spakky.core.interfaces.equatable import EquatableT, IEquatable
from spakky.core.mutability import mutable
from spakky.domain.models.domain_event import DomainEvent
from spakky.domain.models.entity import Entity


@mutable
class AggregateRoot(Entity[EquatableT], Generic[EquatableT], ABC):
    """`AggregateRoot` is a building block for DDD (Domain Driven Design)\n
    You can inherit this to some aggregate root entity\n
    `AggregateRoot` has event resources\n
    you can add/remove/clear domain events
    """

    __events: list[DomainEvent] = field(
        init=False, repr=False, default_factory=list[DomainEvent]
    )

    @property
    def events(self) -> Sequence[DomainEvent]:
        """You can get read-only events from `AggregateRoot`\n
        This event list copied from original events\n
        So if you modify this, then nothing is changed in original events

        Returns:
            Sequence[DomainEvent]: Read-only copied events from `AggregateRoot`
        """
        return deepcopy(self.__events)

    def add_event(self, event: DomainEvent) -> None:
        """Add new event to `AggregateRoot`

        Args:
            event (DomainEvent): Domain event to add to `AggregateRoot`
        """
        self.__events.append(event)

    def remove_event(self, event: DomainEvent) -> None:
        """Remove existing event from `AggregateRoot`

        Args:
            event (DomainEvent): Domain event to remove from `AggregateRoot`
        """
        self.__events.remove(event)

    def clear_events(self) -> None:
        """Clear all events from `AggregateRoot`"""
        self.__events.clear()


AggregateRootT = TypeVar("AggregateRootT", bound=AggregateRoot[IEquatable])
