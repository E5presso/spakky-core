from abc import ABC
from typing import Any, Generic
from dataclasses import field

from spakky.core.interfaces.equatable import EquatableT, IEquatable
from spakky.core.mutability import mutable
from spakky.domain.error import SpakkyDomainError


class MonkeyPatchIsNotAcceptableError(SpakkyDomainError):
    ...


@mutable
class Entity(IEquatable, Generic[EquatableT], ABC):
    id: EquatableT | None = field(default=None)
    __is_setted: bool = field(init=False, default=False)

    @property
    def is_transient(self) -> bool:
        return self.id is None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        if self.is_transient or other.is_transient:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def validate(self) -> None:
        return

    def __post_init__(self) -> None:
        self.validate()
        self.__is_setted = True

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name not in self.__dataclass_fields__:
            raise MonkeyPatchIsNotAcceptableError
        super().__setattr__(__name, __value)
        if self.__is_setted:
            self.validate()
