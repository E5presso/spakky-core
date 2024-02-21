from abc import abstractmethod
from typing import TypeVar, Protocol, runtime_checkable

from typing_extensions import Self


@runtime_checkable
class IEquatable(Protocol):
    """Interface that can be equatable and hashable\n
    This is a protocol for `__eq__` and `__hash__`
    """

    @abstractmethod
    def __eq__(self, __value: Self) -> bool: ...

    @abstractmethod
    def __hash__(self) -> int: ...


EquatableT = TypeVar("EquatableT", bound=IEquatable)
