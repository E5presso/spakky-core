from abc import ABC
from copy import deepcopy
from dataclasses import field
from typing import Any, Generic, Sequence, TypeVar

from spakky.core.interfaces.equatable import EquatableT
from spakky.core.mutability import mutable
from spakky.domain.models.entity import AbstractEntity
from spakky.domain.models.event import AbstractIntegrationEvent


@mutable
class AbstractAggregateRoot(AbstractEntity[EquatableT], Generic[EquatableT], ABC):
    __events: list[AbstractIntegrationEvent] = field(
        init=False, repr=False, default_factory=list[AbstractIntegrationEvent]
    )

    @property
    def events(self) -> Sequence[AbstractIntegrationEvent]:
        return deepcopy(self.__events)

    def add_event(self, event: AbstractIntegrationEvent) -> None:
        self.__events.append(event)

    def remove_event(self, event: AbstractIntegrationEvent) -> None:
        self.__events.remove(event)

    def clear_events(self) -> None:
        self.__events.clear()


AggregateRootT = TypeVar("AggregateRootT", bound=AbstractAggregateRoot[Any])
