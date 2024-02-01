from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Sequence

from spakky.core.interfaces.equatable import EquatableT, IEquatable
from spakky.core.mutability import immutable

ProxyIdT = TypeVar("ProxyIdT", bound=IEquatable)


@immutable
class ProxyModel(IEquatable, Generic[EquatableT], ABC):
    id: EquatableT

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


ProxyModelT = TypeVar("ProxyModelT", bound=ProxyModel[IEquatable])


class IGenericProxy(Generic[ProxyModelT, ProxyIdT], ABC):
    @abstractmethod
    def single(self, proxy_id: ProxyIdT) -> ProxyModelT:
        ...

    @abstractmethod
    def single_or_none(self, proxy_id: ProxyIdT) -> ProxyModelT | None:
        ...

    @abstractmethod
    def contains(self, proxy_id: ProxyIdT) -> bool:
        ...

    @abstractmethod
    def range(self, proxy_ids: Sequence[ProxyIdT]) -> Sequence[ProxyModelT]:
        ...


class IAsyncGenericProxy(Generic[ProxyModelT, ProxyIdT], ABC):
    @abstractmethod
    async def single(self, proxy_id: ProxyIdT) -> ProxyModelT:
        ...

    @abstractmethod
    async def single_or_none(self, proxy_id: ProxyIdT) -> ProxyModelT | None:
        ...

    @abstractmethod
    async def contains(self, proxy_id: ProxyIdT) -> bool:
        ...

    @abstractmethod
    async def range(self, proxy_ids: Sequence[ProxyIdT]) -> Sequence[ProxyModelT]:
        ...
