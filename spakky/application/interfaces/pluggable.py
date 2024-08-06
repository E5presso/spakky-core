from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.application.interfaces.registry import IRegistry


@runtime_checkable
class IPluggable(Protocol):
    @abstractmethod
    def register(self, registry: IRegistry) -> None: ...
