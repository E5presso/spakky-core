from abc import ABC
from typing import Generic

from spakky.core.interfaces.equatable import EquatableT, IEquatable
from spakky.core.mutability import mutable


@mutable
class Entity(IEquatable, Generic[EquatableT], ABC):
    id: EquatableT

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
