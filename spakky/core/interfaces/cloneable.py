import sys
from abc import abstractmethod
from typing import Protocol, TypeVar, runtime_checkable

if sys.version_info >= (3, 11):
    from typing import Self  # pragma: no cover
else:
    from typing_extensions import Self  # pragma: no cover


@runtime_checkable
class ICloneable(Protocol):
    @abstractmethod
    def clone(self) -> Self: ...


CloneableT = TypeVar("CloneableT", bound=ICloneable)
