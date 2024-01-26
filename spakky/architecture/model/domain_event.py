from abc import ABC
from copy import deepcopy
from uuid import UUID, uuid4
from typing import Self
from datetime import datetime
from dataclasses import field

from spakky.core.cloneable import ICloneable
from spakky.core.equatable import IEquatable
from spakky.core.mutability import immutable


@immutable
class DomainEvent(IEquatable, ICloneable, ABC):
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def clone(self) -> Self:
        return deepcopy(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.id == other.id and self.timestamp == other.timestamp

    def __hash__(self) -> int:
        return hash(self.id) ^ hash(self.timestamp)
