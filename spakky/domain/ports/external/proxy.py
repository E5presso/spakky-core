from abc import abstractmethod
from typing import Any, Generic, Protocol, Sequence, TypeVar, runtime_checkable

from spakky.core.interfaces.equatable import IEquatable
from spakky.core.mutability import immutable

ProxyIdT_contra = TypeVar("ProxyIdT_contra", bound=IEquatable, contravariant=True)


@immutable
class ProxyModel(IEquatable, Generic[ProxyIdT_contra]):
    id: ProxyIdT_contra

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


ProxyModelT_co = TypeVar("ProxyModelT_co", bound=ProxyModel[Any], covariant=True)


@runtime_checkable
class IGenericProxy(Protocol[ProxyModelT_co, ProxyIdT_contra]):
    @abstractmethod
    def get(self, proxy_id: ProxyIdT_contra) -> ProxyModelT_co: ...

    @abstractmethod
    def get_or_none(self, proxy_id: ProxyIdT_contra) -> ProxyModelT_co | None: ...

    @abstractmethod
    def contains(self, proxy_id: ProxyIdT_contra) -> bool: ...

    @abstractmethod
    def range(
        self, proxy_ids: Sequence[ProxyIdT_contra]
    ) -> Sequence[ProxyModelT_co]: ...


@runtime_checkable
class IAsyncGenericProxy(Protocol[ProxyModelT_co, ProxyIdT_contra]):
    @abstractmethod
    async def get(self, proxy_id: ProxyIdT_contra) -> ProxyModelT_co: ...

    @abstractmethod
    async def get_or_none(self, proxy_id: ProxyIdT_contra) -> ProxyModelT_co | None: ...

    @abstractmethod
    async def contains(self, proxy_id: ProxyIdT_contra) -> bool: ...

    @abstractmethod
    async def range(
        self, proxy_ids: Sequence[ProxyIdT_contra]
    ) -> Sequence[ProxyModelT_co]: ...
