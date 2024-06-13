from enum import Enum, auto
from dataclasses import field

from spakky.core.mutability import immutable
from spakky.domain.models.value_object import ValueObject


class OrderByOption(str, Enum):
    DEFAULT = auto()
    ASC = auto()
    DESC = auto()


@immutable
class OrderByClause(ValueObject):
    column: str
    order: OrderByOption = field(default=OrderByOption.DEFAULT)


@immutable
class OrderBy(ValueObject):
    clauses: list[OrderByClause] = field(default_factory=list[OrderByClause])
