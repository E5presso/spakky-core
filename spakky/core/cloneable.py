from abc import abstractmethod
from typing import Self, Protocol, runtime_checkable


@runtime_checkable
class ICloneable(Protocol):
    @abstractmethod
    def clone(self) -> Self:
        ...
