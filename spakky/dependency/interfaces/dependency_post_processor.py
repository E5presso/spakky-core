from abc import abstractmethod
from typing import Any, Protocol, runtime_checkable

from spakky.dependency.interfaces.dependency_container import IDependencyContainer


@runtime_checkable
class IDependencyPostProcessor(Protocol):
    @abstractmethod
    def process_dependency(self, container: IDependencyContainer, dependency: Any) -> Any:
        ...
