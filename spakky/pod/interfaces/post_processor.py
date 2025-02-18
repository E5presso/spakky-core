from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class IPostProcessor(Protocol):
    @abstractmethod
    def post_process(self, pod: object) -> object: ...
