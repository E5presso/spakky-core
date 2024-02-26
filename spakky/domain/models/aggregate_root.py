from abc import ABC
from copy import deepcopy
from typing import Any, Generic, TypeVar, Sequence
from dataclasses import field

from spakky.core.interfaces.equatable import EquatableT
from spakky.core.mutability import mutable
from spakky.domain.models.domain_event import DomainEvent
from spakky.domain.models.entity import Entity


@mutable
class AggregateRoot(Entity[EquatableT], Generic[EquatableT], ABC):
    __events: list[DomainEvent] = field(init=False, repr=False, default_factory=list)

    @property
    def events(self) -> Sequence[DomainEvent]:
        return deepcopy(self.__events)

    def add_event(self, event: DomainEvent) -> None:
        self.__events.append(event)

    def remove_event(self, event: DomainEvent) -> None:
        self.__events.remove(event)

    def clear_events(self) -> None:
        self.__events.clear()


AggregateRootT = TypeVar("AggregateRootT", bound=AggregateRoot[Any])
