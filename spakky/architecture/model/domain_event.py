from abc import ABC
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import field

from spakky.core.equatable import IEquatable
from spakky.core.mutability import immutable


@immutable
class DomainEvent(IEquatable, ABC):
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.id == other.id

    def __ne__(self, __value: object) -> bool:
        return not self == __value

    def __hash__(self) -> int:
        return hash(self.id)
