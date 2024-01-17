from abc import ABC, abstractmethod
from typing import Callable, Sequence

from spakky.core.generics import ObjectT


class IDependencyContainer(ABC):
    @abstractmethod
    def register(self, dependency: type) -> None:
        ...

    @abstractmethod
    def exists(self, dependency: type) -> bool:
        ...

    @abstractmethod
    def retrieve(self, dependency: type[ObjectT]) -> ObjectT:
        ...

    @abstractmethod
    def query(self, selector: Callable[[type], bool]) -> Sequence[type]:
        ...

    @abstractmethod
    def all(self) -> Sequence[type]:
        ...
