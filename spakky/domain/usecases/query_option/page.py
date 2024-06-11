from abc import ABC
from typing import Generic, TypeVar

from spakky.core.interfaces.equatable import EquatableT
from spakky.core.mutability import immutable
from spakky.domain.models.value_object import ValueObject


@immutable
class Pageable(ValueObject, ABC):
    limit: int


@immutable
class OffsetBasedPage(Pageable, ValueObject):
    offset: int


@immutable
class CursorBasedPage(Pageable, ValueObject):
    cursor: str


@immutable
class KeysetBasedPage(Pageable, ValueObject, Generic[EquatableT]):
    last_key: EquatableT


PageableT = TypeVar("PageableT", bound=Pageable)
