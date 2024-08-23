from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.application.interfaces.container import IPodContainer


@runtime_checkable
class IPodPostProcessor(Protocol):
    @abstractmethod
    def post_process(self, container: IPodContainer, pod: object) -> object: ...
