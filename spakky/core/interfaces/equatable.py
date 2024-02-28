import sys
from abc import abstractmethod
from typing import TypeVar, Protocol, runtime_checkable

if sys.version_info >= (3, 11):
    from typing import Self  # pragma: no cover
else:
    from typing_extensions import Self  # pragma: no cover


@runtime_checkable
class IEquatable(Protocol):
    @abstractmethod
    def __eq__(self, __value: Self) -> bool:
        ...

    @abstractmethod
    def __hash__(self) -> int:
        ...


EquatableT = TypeVar("EquatableT", bound=IEquatable)
