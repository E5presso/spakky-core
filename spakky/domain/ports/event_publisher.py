from abc import ABC, abstractmethod
from typing import Generic

from spakky.domain.models.aggregate_root import AggregateRootT


class IGenericEventPublisher(Generic[AggregateRootT], ABC):
    @abstractmethod
    def publish(self, aggregate: AggregateRootT) -> None:
        ...


class IAsyncGenericEventPublisher(Generic[AggregateRootT], ABC):
    @abstractmethod
    async def publish(self, aggregate: AggregateRootT) -> None:
        ...
