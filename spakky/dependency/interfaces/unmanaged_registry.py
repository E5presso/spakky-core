from abc import abstractmethod
from typing import Any, Callable, Protocol, runtime_checkable

from spakky.core.generics import ObjectT


@runtime_checkable
class IUnmanagedRegistry(Protocol):
    @abstractmethod
    def register_factory(self, name: str, factory: Callable[[], ObjectT]) -> None:
        ...

    @abstractmethod
    def register_dependency(self, name: str, dependency: Any) -> None:
        ...
