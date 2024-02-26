import sys
from abc import abstractmethod
from typing import TypeVar, Protocol, runtime_checkable

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


@runtime_checkable
class ICloneable(Protocol):
    @abstractmethod
    def clone(self) -> Self:
        ...


CloneableT = TypeVar("CloneableT", bound=ICloneable)
