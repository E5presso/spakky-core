from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class IEquatable(Protocol):
    @abstractmethod
    def __eq__(self, __value: object) -> bool:
        ...

    @abstractmethod
    def __hash__(self) -> int:
        ...
