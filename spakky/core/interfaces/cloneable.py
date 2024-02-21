from abc import abstractmethod
from typing import TypeVar, Protocol, runtime_checkable

from typing_extensions import Self


@runtime_checkable
class ICloneable(Protocol):
    """Interface that can clone from original object\n
    This is a protocol for deep copying object
    """

    @abstractmethod
    def clone(self) -> Self:
        """Clone(deep copy) object

        Returns:
            Self: Cloned object from the origin
        """
        ...


CloneableT = TypeVar("CloneableT", bound=ICloneable)
