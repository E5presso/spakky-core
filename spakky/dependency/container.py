from abc import ABC, abstractmethod
from typing import Sequence

from spakky.core.generics import ObjectT
from spakky.dependency.dependency import Dependency


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
    def query(self, annotation: type[Dependency]) -> Sequence[type]:
        ...

    @abstractmethod
    def all(self) -> Sequence[type]:
        ...
