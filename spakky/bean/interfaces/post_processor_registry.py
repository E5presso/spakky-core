from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.bean.interfaces.post_processor import IBeanPostProcessor


@runtime_checkable
class IBeanPostProcessorRegistry(Protocol):
    @abstractmethod
    def register_bean_post_processor(self, post_processor: IBeanPostProcessor) -> None:
        ...
