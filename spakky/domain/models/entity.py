from abc import ABC, abstractmethod
from typing import Any, Generic
from dataclasses import field

from spakky.core.interfaces.equatable import EquatableT, IEquatable
from spakky.core.mutability import mutable
from spakky.domain.error import SpakkyDomainError


class CannotMonkeyPatchEntityError(SpakkyDomainError): ...


@mutable
class Entity(IEquatable, Generic[EquatableT], ABC):
    uid: EquatableT
    __initialized: bool = field(init=False, repr=False, default=False)

    @classmethod
    @abstractmethod
    def next_id(cls) -> EquatableT: ...

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

    def validate(self) -> None:
        return
