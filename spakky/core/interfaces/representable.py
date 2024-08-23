from abc import abstractmethod
from typing import TypeVar, Protocol, runtime_checkable


@runtime_checkable
class IRepresentable(Protocol):
    @abstractmethod
    def __str__(self) -> str: ...

    @abstractmethod
    def __repr__(self) -> str: ...


RepresentableT = TypeVar("RepresentableT", bound=IRepresentable)
