from abc import abstractmethod
from typing import Any, Protocol, runtime_checkable

from spakky.bean.interfaces.bean_container import IBeanContainer


@runtime_checkable
class IBeanPostProcessor(Protocol):
    @abstractmethod
    def post_process(self, container: IBeanContainer, bean: Any) -> Any:
        ...
