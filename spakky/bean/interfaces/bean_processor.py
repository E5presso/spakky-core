from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.bean.interfaces.bean_container import IBeanContainer


@runtime_checkable
class IBeanPostProcessor(Protocol):
    @abstractmethod
    def post_process_bean(self, container: IBeanContainer, bean: object) -> object: ...
