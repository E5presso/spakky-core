from abc import abstractmethod
from typing import Callable, Protocol, overload, runtime_checkable

from spakky.core.types import ObjectT
from spakky.pod.annotations.pod import Pod, PodType
from spakky.pod.error import AbstractSpakkyPodError
from spakky.pod.interfaces.post_processor import IPostProcessor


class CircularDependencyGraphDetectedError(AbstractSpakkyPodError):
    message = "Circular dependency detected"


class NoSuchPodError(AbstractSpakkyPodError):
    message = "Cannot find pod from context by given condition"


class NoUniquePodError(AbstractSpakkyPodError):
    message = "Multiple pod found by given condition"


class CannotRegisterNonPodObjectError(AbstractSpakkyPodError):
    message = "Cannot register a non-pod object"


class PodNameAlreadyExistsError(AbstractSpakkyPodError):
    message = "Pod name already exists"


@runtime_checkable
class IContainer(Protocol):
    @property
    @abstractmethod
    def pods(self) -> dict[str, Pod]: ...

    @abstractmethod
    def add(self, obj: PodType) -> None: ...

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
