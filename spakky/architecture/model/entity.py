from abc import ABC
from copy import deepcopy
from typing import Generic, Sequence
from dataclasses import field

from spakky.architecture.model.domain_event import DomainEvent
from spakky.core.equatable import IEquatable
from spakky.core.generics import EquatableT
from spakky.core.mutability import mutable


@mutable
class Entity(IEquatable, Generic[EquatableT], ABC):
    id: EquatableT
    _events: list[DomainEvent] = field(
        init=False, default_factory=list[DomainEvent], repr=False
    )

    @property
    def events(self) -> Sequence[DomainEvent]:
        return deepcopy(self._events)

    def add_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def remove_event(self, event: DomainEvent) -> None:
        self._events.remove(event)

    def clear_events(self) -> None:
        self._events.clear()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
