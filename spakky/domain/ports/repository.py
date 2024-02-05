from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Sequence

from spakky.core.interfaces.equatable import IEquatable
from spakky.domain.models.aggregate_root import AggregateRootT

AggregateIdT = TypeVar("AggregateIdT", bound=IEquatable)


class IGenericRepository(Generic[AggregateRootT, AggregateIdT], ABC):
    @abstractmethod
    def single(self, aggregate_id: AggregateIdT) -> AggregateRootT:
        ...

    @abstractmethod
    def single_or_none(self, aggregate_id: AggregateIdT) -> AggregateRootT | None:
        ...

    @abstractmethod
    def contains(self, aggregate_id: AggregateIdT) -> bool:
        ...

    @abstractmethod
    def range(self, aggregate_ids: Sequence[AggregateIdT]) -> Sequence[AggregateRootT]:
        ...

    @abstractmethod
    def save(self, aggregate: AggregateRootT) -> AggregateRootT:
        ...

    @abstractmethod
    def save_all(self, aggregates: Sequence[AggregateRootT]) -> Sequence[AggregateRootT]:
        ...

    @abstractmethod
    def delete(self, aggregate: AggregateRootT) -> AggregateRootT:
        ...

    @abstractmethod
    def delete_all(
        self, aggregates: Sequence[AggregateRootT]
    ) -> Sequence[AggregateRootT]:
        ...


class IAsyncGenericRepository(Generic[AggregateRootT, AggregateIdT], ABC):
    @abstractmethod
    async def single(self, aggregate_id: AggregateIdT) -> AggregateRootT:
        ...

    @abstractmethod
    async def single_or_none(self, aggregate_id: AggregateIdT) -> AggregateRootT | None:
        ...

    @abstractmethod
    async def contains(self, aggregate_id: AggregateIdT) -> bool:
        ...

    @abstractmethod
    async def range(
        self, aggregate_ids: Sequence[AggregateIdT]
    ) -> Sequence[AggregateRootT]:
        ...

    @abstractmethod
    async def save(self, aggregate: AggregateRootT) -> AggregateRootT:
        ...

    @abstractmethod
    async def save_all(
        self, aggregates: Sequence[AggregateRootT]
    ) -> Sequence[AggregateRootT]:
        ...

    @abstractmethod
    async def delete(self, aggregate: AggregateRootT) -> AggregateRootT:
        ...

    @abstractmethod
    async def delete_all(
        self, aggregates: Sequence[AggregateRootT]
    ) -> Sequence[AggregateRootT]:
        ...
