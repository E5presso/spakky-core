from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.application.interfaces.container import IContainer


@runtime_checkable
class IPlugin(Protocol):
    @abstractmethod
    def register(self, container: IContainer) -> None: ...


@runtime_checkable
class IPluginRegistry(Protocol):
    @abstractmethod
    def register_plugin(self, plugin: IPlugin) -> None: ...
