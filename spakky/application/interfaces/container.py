from abc import abstractmethod
from typing import Any, Callable, Protocol, Sequence, overload, runtime_checkable

from spakky.core.types import AnyT
from spakky.injectable.error import SpakkyInjectableError


class NoSuchInjectableError(SpakkyInjectableError):
    message = "Cannot find injectable from context by given condition"


class NoUniqueInjectableError(SpakkyInjectableError):
    message = "Multiple injectable found by given condition"


@runtime_checkable
class IContainer(Protocol):
    @overload
    @abstractmethod
    def contains(self, *, type_: type) -> bool: ...

    @overload
    @abstractmethod
    def contains(self, *, name: str) -> bool: ...

    @abstractmethod
    def contains(
        self,
        type_: type | None = None,
        name: str | None = None,
    ) -> bool: ...

    @overload
    @abstractmethod
    def get(self, *, type_: type[AnyT]) -> AnyT: ...

    @overload
    @abstractmethod
    def get(self, *, name: str) -> Any: ...

    @abstractmethod
    def get(
        self,
        type_: type[AnyT] | None = None,
        name: str | None = None,
    ) -> AnyT | Any: ...

    @abstractmethod
    def filter_injectable_types(
        self,
        clause: Callable[[type], bool],
    ) -> Sequence[type]: ...

    @abstractmethod
    def filter_injectables(self, clause: Callable[[type], bool]) -> Sequence[object]: ...
