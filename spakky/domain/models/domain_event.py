from abc import ABC
from copy import deepcopy
from uuid import UUID, uuid4
from typing import Self
from datetime import datetime
from dataclasses import field

from spakky.core.interfaces.cloneable import ICloneable
from spakky.core.interfaces.comparable import IComparable
from spakky.core.interfaces.equatable import IEquatable
from spakky.core.mutability import immutable


@immutable
class DomainEvent(IEquatable, IComparable, ICloneable, ABC):
    """`DomainEvent` is a building block for DDD (Domain Driven Design)\n
    You can inherit this to some custom domain event\n
    `DomainEvent` has unique event id and timestamp\n
    This is immutable(frozen) object. So you cannot modify them.
    """

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

    def __lt__(self, __value: Self) -> bool:
        return self.timestamp < __value.timestamp

    def __le__(self, __value: Self) -> bool:
        return self.timestamp <= __value.timestamp

    def __gt__(self, __value: Self) -> bool:
        return self.timestamp > __value.timestamp

    def __ge__(self, __value: Self) -> bool:
        return self.timestamp >= __value.timestamp
