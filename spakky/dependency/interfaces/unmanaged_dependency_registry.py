from abc import abstractmethod
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class IUnmanagedDependencyRegistry(Protocol):
    @abstractmethod
    def register_unmanaged_dependency(self, name: str, dependency: Any) -> None:
        ...
