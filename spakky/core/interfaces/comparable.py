import sys
from abc import abstractmethod
from typing import Protocol, TypeVar, runtime_checkable

if sys.version_info >= (3, 11):
    from typing import Self  # pragma: no cover
else:
    from typing_extensions import Self  # pragma: no cover


@runtime_checkable
class IComparable(Protocol):
    @abstractmethod
    def __lt__(self, __value: Self) -> bool: ...

    @abstractmethod
    def __le__(self, __value: Self) -> bool: ...

    @abstractmethod
    def __gt__(self, __value: Self) -> bool: ...

    @abstractmethod
    def __ge__(self, __value: Self) -> bool: ...


ComparableT = TypeVar("ComparableT", bound=IComparable)
