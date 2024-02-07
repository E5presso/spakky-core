from abc import abstractmethod
from types import ModuleType
from typing import Protocol, runtime_checkable


@runtime_checkable
class IManagedDependencyScanner(Protocol):
    @abstractmethod
    def scan(self, package: ModuleType) -> None:
        """Auto-scan from given package-module

        Args:
            package (ModuleType): package-module to start full-scan components
        """
        ...
