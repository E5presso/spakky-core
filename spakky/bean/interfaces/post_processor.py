from abc import abstractmethod
from typing import Any, Protocol, runtime_checkable

from spakky.bean.interfaces.bean_container import IBeanContainer


@runtime_checkable
class IBeanPostProcessor(Protocol):
    @abstractmethod
    def process_bean(self, container: IBeanContainer, bean: Any) -> Any:
        ...


@runtime_checkable
class IBeanPostPrecessorRegistry(Protocol):
    @abstractmethod
    def register_post_processor(self, post_processor: IBeanPostProcessor) -> None:
        ...
