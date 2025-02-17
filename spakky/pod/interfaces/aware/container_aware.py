from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.pod.interfaces.aware.aware import IAware
from spakky.pod.interfaces.container import IContainer


@runtime_checkable
class IContainerAware(IAware, Protocol):
    @abstractmethod
    def set_container(self, container: IContainer) -> None: ...
