from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.core.interfaces.equatable import EquatableT
from spakky.domain.models.aggregate_root import AggregateRoot


@runtime_checkable
class IEventPublisher(Protocol[EquatableT]):
    @abstractmethod
    def publish(self, aggregate: AggregateRoot[EquatableT]) -> None:
        ...


@runtime_checkable
class IAsyncEventPublisher(Protocol[EquatableT]):
    @abstractmethod
    async def publish(self, aggregate: AggregateRoot[EquatableT]) -> None:
        ...
