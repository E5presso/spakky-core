from abc import abstractmethod
from typing import Callable, Protocol, runtime_checkable

from spakky.application.error import SpakkyApplicationError
from spakky.application.interfaces.post_processor import IPostProcessor
from spakky.core.types import ObjectT
from spakky.pod.error import SpakkyPodError
from spakky.pod.pod import Pod, PodType


class CannotRegisterNonPodObjectError(SpakkyPodError):
    message = "Cannot register non-pod object."


class NoSuchPodError(SpakkyApplicationError):
    message = "Cannot find pod from context by given condition"


class NoUniquePodError(SpakkyApplicationError):
    message = "Multiple pod found by given condition"


@runtime_checkable
class IContainer(Protocol):
    @property
    @abstractmethod
    def pods(self) -> set[PodType]: ...

    @property
    @abstractmethod
    def post_processors(self) -> set[type[IPostProcessor]]: ...

    @abstractmethod
    def register(self, obj: PodType) -> None: ...

    @abstractmethod
    def register_post_processor(self, post_processor: IPostProcessor) -> None: ...

    @abstractmethod
    def get(self, type_: type[ObjectT], name: str | None = None) -> ObjectT: ...

    @abstractmethod
    def all(self, type_: type[ObjectT]) -> dict[str, ObjectT]: ...

    @abstractmethod
    def contains(self, type_: type, name: str | None = None) -> bool: ...

    @abstractmethod
    def find(self, selector: Callable[[Pod], bool]) -> dict[str, object]: ...
