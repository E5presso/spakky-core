import sys
from abc import ABC
from copy import deepcopy
from dataclasses import field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from spakky.core.interfaces.cloneable import ICloneable
from spakky.core.interfaces.comparable import IComparable
from spakky.core.interfaces.equatable import IEquatable
from spakky.core.mutability import immutable

if sys.version_info >= (3, 11):
    from typing import Self  # pragma: no cover
else:
    from typing_extensions import Self  # pragma: no cover


@immutable
class AbstractDomainEvent(IEquatable, IComparable, ICloneable, ABC):
    event_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def event_name(self) -> str:
        return type(self).__name__

    def clone(self) -> Self:
        return deepcopy(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.event_id == other.event_id and self.timestamp == other.timestamp

    def __hash__(self) -> int:
        return hash(self.event_id) ^ hash(self.timestamp)

    def __lt__(self, __value: Self) -> bool:
        return self.timestamp < __value.timestamp

    def __le__(self, __value: Self) -> bool:
        return self.timestamp <= __value.timestamp

    def __gt__(self, __value: Self) -> bool:
        return self.timestamp > __value.timestamp

    def __ge__(self, __value: Self) -> bool:
        return self.timestamp >= __value.timestamp


@immutable
class AbstractIntegrationEvent(AbstractDomainEvent, ABC): ...
