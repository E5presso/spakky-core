from abc import abstractmethod
from typing import Callable, Protocol, overload, runtime_checkable

from spakky.core.types import ObjectT
from spakky.pod.annotations.pod import Pod, PodType
from spakky.pod.error import AbstractSpakkyPodError


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

    @overload
    @abstractmethod
    def get(self, type_: type[ObjectT]) -> ObjectT: ...

    @overload
    @abstractmethod
    def get(self, type_: type[ObjectT], name: str) -> ObjectT: ...

    @abstractmethod
    def get(
        self,
        type_: type[ObjectT],
        name: str | None = None,
    ) -> ObjectT | object: ...

    @overload
    @abstractmethod
    def contains(self, type_: type) -> bool: ...

    @overload
    @abstractmethod
    def contains(self, type_: type, name: str) -> bool: ...

    @abstractmethod
    def contains(
        self,
        type_: type,
        name: str | None = None,
    ) -> bool: ...

    @abstractmethod
    def find(self, selector: Callable[[Pod], bool]) -> set[object]: ...
