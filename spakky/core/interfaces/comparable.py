from abc import abstractmethod
from typing import Self, TypeVar, Protocol, runtime_checkable


@runtime_checkable
class IComparable(Protocol):
    @abstractmethod
    def __lt__(self, __value: Self) -> bool:
        ...

    @abstractmethod
    def __le__(self, __value: Self) -> bool:
        ...

    @abstractmethod
    def __gt__(self, __value: Self) -> bool:
        ...

    @abstractmethod
    def __ge__(self, __value: Self) -> bool:
        ...


ComparableT = TypeVar("ComparableT", bound=IComparable)
