from abc import ABC, abstractmethod

from spakky.core.interfaces.equatable import EquatableT
from spakky.domain.models.aggregate_root import AggregateRoot


class IEventPublisher(ABC):
    @abstractmethod
    def publish(self, aggregate: AggregateRoot[EquatableT]) -> None:
        ...


class IAsyncEventPublisher(ABC):
    @abstractmethod
    async def publish(self, aggregate: AggregateRoot[EquatableT]) -> None:
        ...
