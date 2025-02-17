from abc import abstractmethod
from typing import Callable, Protocol, overload, runtime_checkable

from spakky.core.types import ObjectT
from spakky.pod.error import SpakkyPodError
from spakky.pod.interfaces.post_processor import IPostProcessor
from spakky.pod.pod import Pod, PodType


class CircularDependencyGraphDetectedError(SpakkyPodError):
    message = "Circular dependency detected"


class NoSuchPodError(SpakkyPodError):
    message = "Cannot find pod from context by given condition"


class NoUniquePodError(SpakkyPodError):
    message = "Multiple pod found by given condition"


class CannotRegisterNonPodObjectError(SpakkyPodError):
    message = "Cannot register a non-pod object"


class PodNameAlreadyExistsError(SpakkyPodError):
    message = "Pod name already exists"


@runtime_checkable
class IContainer(Protocol):
    @property
    @abstractmethod
    def pods(self) -> dict[str, Pod]: ...

    @abstractmethod
    def add(self, obj: PodType) -> None: ...

    @abstractmethod
    def add_singleton_instance(self, name: str, obj: object) -> None: ...

    @abstractmethod
    def _add_post_processor(self, post_processor: IPostProcessor) -> None: ...

    @overload
    @abstractmethod
    def get(self, *, name: str) -> object: ...

    @overload
    @abstractmethod
    def get(self, *, type_: type[ObjectT]) -> ObjectT: ...

    @overload
    @abstractmethod
    def get(self, *, name: str, type_: type[ObjectT]) -> ObjectT: ...

    @abstractmethod
    def get(
        self,
        name: str | None = None,
        type_: type[ObjectT] | None = None,
    ) -> ObjectT | object: ...

    @overload
    @abstractmethod
    def contains(self, *, name: str) -> bool: ...

    @overload
    @abstractmethod
    def contains(self, *, type_: type) -> bool: ...

    @overload
    @abstractmethod
    def contains(self, *, name: str, type_: type) -> bool: ...

    @abstractmethod
    def contains(
        self,
        name: str | None = None,
        type_: type | None = None,
    ) -> bool: ...

    @abstractmethod
    def find(self, selector: Callable[[Pod], bool]) -> set[object]: ...
