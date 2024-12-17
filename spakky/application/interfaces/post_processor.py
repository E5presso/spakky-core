from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from spakky.application.interfaces.container import IContainer


@runtime_checkable
class IPostProcessor(Protocol):
    @abstractmethod
    def post_process(self, container: "IContainer", pod: object) -> object: ...
