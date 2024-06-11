from abc import abstractmethod
from typing import Any, Generic, TypeVar, Protocol, runtime_checkable

from spakky.domain.models.aggregate_root import AggregateRoot

AggregateRootT_contra = TypeVar(
    "AggregateRootT_contra", bound=AggregateRoot[Any], contravariant=True
)


@runtime_checkable
class IEventPublisher(Generic[AggregateRootT_contra], Protocol):
    @abstractmethod
    def publish(self, aggregate: AggregateRootT_contra) -> None: ...


@runtime_checkable
class IAsyncEventPublisher(Generic[AggregateRootT_contra], Protocol):
    @abstractmethod
    async def publish(self, aggregate: AggregateRootT_contra) -> None: ...
