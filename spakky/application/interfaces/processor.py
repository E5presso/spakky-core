from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.application.interfaces.container import IContainer


@runtime_checkable
class IPostProcessor(Protocol):
    @abstractmethod
    def post_process(self, container: IContainer, injectable: object) -> object: ...
