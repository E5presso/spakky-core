import sys
from abc import ABC, abstractmethod
from dataclasses import field
from datetime import datetime, timedelta
from typing import Any, Generic
from uuid import UUID, uuid4

from spakky.core.interfaces.equatable import EquatableT, IEquatable
from spakky.core.mutability import mutable
from spakky.domain.error import AbstractSpakkyDomainError

if sys.version_info >= (3, 11):  # pragma: no cover
    from datetime import UTC
else:  # pragma: no cover
    from datetime import timezone

    UTC = timezone(offset=timedelta(hours=0), name="UTC")


class CannotMonkeyPatchEntityError(AbstractSpakkyDomainError):
    message = "Cannot monkey patch an entity."


@mutable
class AbstractEntity(IEquatable, Generic[EquatableT], ABC):
    __initialized: bool = field(init=False, repr=False, default=False)

    uid: EquatableT
    version: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    @abstractmethod
    def next_id(cls) -> EquatableT: ...

    @abstractmethod
    def validate(self) -> None: ...

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.uid == other.uid

    def __hash__(self) -> int:
        return hash(self.uid)

    def __post_init__(self) -> None:
        self.validate()
        self.__initialized = True

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name not in self.__dataclass_fields__:
            raise CannotMonkeyPatchEntityError
        __old: Any | None = getattr(self, __name, None)
        super().__setattr__(__name, __value)
        if self.__initialized:
            try:
                self.validate()
            except:
                super().__setattr__(__name, __old)
                raise
