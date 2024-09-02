from abc import abstractmethod
from typing import Callable, Protocol, runtime_checkable

from spakky.application.error import SpakkyApplicationError
from spakky.core.types import ObjectT
from spakky.pod.pod import Pod


class NoSuchPodError(SpakkyApplicationError):
    message = "Cannot find pod from context by given condition"


class NoUniquePodError(SpakkyApplicationError):
    message = "Multiple pod found by given condition"


@runtime_checkable
class IPodContainer(Protocol):
    @abstractmethod
    def get(self, type_: type[ObjectT], name: str | None = None) -> ObjectT: ...

    @abstractmethod
    def contains(self, type_: type, name: str | None = None) -> bool: ...

    @abstractmethod
    def find(self, selector: Callable[[Pod], bool]) -> dict[str, object]: ...
