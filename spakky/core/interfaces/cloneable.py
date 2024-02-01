from abc import abstractmethod
from typing import Self, TypeVar, Protocol, runtime_checkable


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
