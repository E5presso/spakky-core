from abc import ABC, abstractmethod
from typing import Any, Generic
from dataclasses import field

from spakky.core.interfaces.equatable import EquatableT, IEquatable
from spakky.core.mutability import mutable
from spakky.domain.error import SpakkyDomainError


class CannotMonkeyPatchEntityError(SpakkyDomainError):
    ...


@mutable
class Entity(IEquatable, Generic[EquatableT], ABC):
    id: EquatableT
    __is_setted: bool = field(init=False, repr=False, default=False)

    @classmethod
    @abstractmethod
    def next_id(cls) -> EquatableT:
        ...

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __post_init__(self) -> None:
        self.validate()
        self.__is_setted = True

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name not in self.__dataclass_fields__:
            raise CannotMonkeyPatchEntityError
        super().__setattr__(__name, __value)
        if self.__is_setted:
            self.validate()

    def validate(self) -> None:
        return
