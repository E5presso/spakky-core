from enum import Enum
from typing import Sequence
from dataclasses import field

from spakky.core.mutability import immutable
from spakky.domain.models.value_object import ValueObject


class OrderByOption(str, Enum):
    ASC = "asc"
    DESC = "desc"


@immutable
class OrderByClause(ValueObject):
    field: str
    order: OrderByOption


@immutable
class OrderBy(ValueObject):
    clauses: Sequence[OrderByClause] = field(default_factory=list[OrderByClause])
