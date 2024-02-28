from abc import abstractmethod
from typing import TypeVar, Protocol, Sequence, runtime_checkable

from spakky.core.interfaces.equatable import IEquatable
from spakky.domain.error import SpakkyDomainError
from spakky.domain.models.aggregate_root import AggregateRootT

AggregateIdT_contra = TypeVar("AggregateIdT_contra", bound=IEquatable, contravariant=True)


class EntityNotFoundError(SpakkyDomainError):
    message = "Entity not found by given id"


@runtime_checkable
class IGenericRepository(Protocol[AggregateRootT, AggregateIdT_contra]):
    @abstractmethod
    def single(self, aggregate_id: AggregateIdT_contra) -> AggregateRootT:
        ...

    @abstractmethod
    def single_or_none(self, aggregate_id: AggregateIdT_contra) -> AggregateRootT | None:
        ...

    @abstractmethod
    def contains(self, aggregate_id: AggregateIdT_contra) -> bool:
        ...

    @abstractmethod
    def range(
        self, aggregate_ids: Sequence[AggregateIdT_contra]
    ) -> Sequence[AggregateRootT]:
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


@runtime_checkable
class IAsyncGenericRepository(Protocol[AggregateRootT, AggregateIdT_contra]):
    @abstractmethod
    async def single(self, aggregate_id: AggregateIdT_contra) -> AggregateRootT:
        ...

    @abstractmethod
    async def single_or_none(
        self, aggregate_id: AggregateIdT_contra
    ) -> AggregateRootT | None:
        ...

    @abstractmethod
    async def contains(self, aggregate_id: AggregateIdT_contra) -> bool:
        ...

    @abstractmethod
    async def range(
        self, aggregate_ids: Sequence[AggregateIdT_contra]
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
