from abc import ABC, abstractmethod
from typing import Callable, Sequence, overload

from spakky.core.generics import ObjectT


class IComponentContainer(ABC):
    @overload
    @abstractmethod
    def register(self, *, dependency: type) -> None:
        ...

    @overload
    @abstractmethod
    def register(self, *, dependency: type, name: str) -> None:
        ...

    @overload
    @abstractmethod
    def contains(self, *, name: str) -> bool:
        ...

    @overload
    @abstractmethod
    def contains(self, *, required_type: type) -> bool:
        ...

    @overload
    @abstractmethod
    def get(self, *, name: str) -> object:
        ...

    @overload
    @abstractmethod
    def get(self, *, required_type: type[ObjectT]) -> ObjectT:
        ...

    @abstractmethod
    def where(self, clause: Callable[[type], bool]) -> Sequence[object]:
        ...

    @abstractmethod
    def all(self) -> Sequence[object]:
        ...
