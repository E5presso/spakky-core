from abc import ABC
from copy import deepcopy
from typing import Generic, Sequence
from dataclasses import field

from spakky.architecture.model.domain_event import DomainEvent
from spakky.architecture.model.entity import Entity
from spakky.core.generics import EquatableT
from spakky.core.mutability import mutable


@mutable
class IAggregateRoot(Entity[EquatableT], Generic[EquatableT], ABC):
    __events: list[DomainEvent] = field(
        init=False, repr=False, default_factory=list[DomainEvent]
    )

    @property
    def events(self) -> Sequence[DomainEvent]:
        return deepcopy(self.__events)

    def add_event(self, event: DomainEvent) -> None:
        self.__events.append(event)

    def remove_event(self, event: DomainEvent) -> None:
        self.__events.remove(event)

    def clear_events(self) -> None:
        self.__events.clear()
