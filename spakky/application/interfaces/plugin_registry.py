from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.application.interfaces.pluggable import IPluggable


@runtime_checkable
class IPluginRegistry(Protocol):
    @abstractmethod
    def register_plugin(self, plugin: IPluggable) -> None: ...
