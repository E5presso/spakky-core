from abc import abstractmethod
from types import ModuleType
from typing import Protocol, runtime_checkable


@runtime_checkable
class IBeanScanner(Protocol):
    @abstractmethod
    def scan(self, package: ModuleType) -> None:
        ...
