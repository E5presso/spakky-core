from abc import abstractmethod
from typing import Any, Callable, Protocol, Sequence, overload, runtime_checkable

from spakky.bean.error import SpakkyBeanError
from spakky.core.types import AnyT


class NoSuchBeanError(SpakkyBeanError):
    message = "Cannot find bean from context by given condition"


class NoUniqueBeanError(SpakkyBeanError):
    message = "Multiple bean found by given condition"


@runtime_checkable
class IBeanContainer(Protocol):
    @overload
    @abstractmethod
    def contains(self, *, required_type: type) -> bool: ...

    @overload
    @abstractmethod
    def contains(self, *, name: str) -> bool: ...

    @abstractmethod
    def contains(
        self, required_type: type | None = None, name: str | None = None
    ) -> bool: ...

    @overload
    @abstractmethod
    def single(self, *, required_type: type[AnyT]) -> AnyT: ...

    @overload
    @abstractmethod
    def single(self, *, name: str) -> Any: ...

    @abstractmethod
    def single(
        self, required_type: type[AnyT] | None = None, name: str | None = None
    ) -> AnyT | Any: ...

    @abstractmethod
    def filter_bean_types(self, clause: Callable[[type], bool]) -> Sequence[type]: ...

    @abstractmethod
    def filter_beans(self, clause: Callable[[type], bool]) -> Sequence[object]: ...
