from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.application.interfaces.post_processor import IPodPostProcessor
from spakky.pod.error import SpakkyPodError
from spakky.pod.pod import PodType


class CannotRegisterNonPodObjectError(SpakkyPodError):
    message = "Cannot register non-pod object."


@runtime_checkable
class IPodRegistry(Protocol):
    @property
    @abstractmethod
    def pods(self) -> set[PodType]: ...

    @property
    @abstractmethod
    def post_processors(self) -> set[type[IPodPostProcessor]]: ...

    @abstractmethod
    def register(self, obj: PodType) -> None: ...

    @abstractmethod
    def register_post_processor(self, post_processor: IPodPostProcessor) -> None: ...
