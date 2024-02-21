from abc import abstractmethod
from typing import Any, Callable, Protocol, Sequence, overload, runtime_checkable

from spakky.bean.error import SpakkyBeanError
from spakky.core.generics import AnyT


class NoSuchBeanError(SpakkyBeanError):
    message = "Cannot find bean from context by given condition"


class NoUniqueBeanError(SpakkyBeanError):
    message = "Multiple bean found by given condition"


@runtime_checkable
class IBeanContainer(Protocol):
    @overload
    @abstractmethod
    def contains(self, *, required_type: type) -> bool:
        ...

    @overload
    @abstractmethod
    def contains(self, *, name: str) -> bool:
        ...

    @abstractmethod
    def contains(
        self, required_type: type | None = None, name: str | None = None
    ) -> bool:
        ...

    @overload
    @abstractmethod
    def get(self, *, required_type: type[AnyT]) -> AnyT:
        ...

    @overload
    @abstractmethod
    def get(self, *, name: str) -> Any:
        ...

    @abstractmethod
    def get(
        self, required_type: type[AnyT] | None = None, name: str | None = None
    ) -> AnyT | Any:
        ...

    @abstractmethod
    def where(self, clause: Callable[[type], bool]) -> Sequence[object]:
        ...
