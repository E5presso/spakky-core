from enum import Enum, auto
from typing import Any, Generic
from dataclasses import field

from spakky.core.interfaces.comparable import IComparable
from spakky.core.interfaces.equatable import IEquatable
from spakky.core.mutability import immutable
from spakky.core.types import AnyT
from spakky.domain.models.value_object import ValueObject
from spakky.domain.usecases.criteria.error import InvalidWhereClauseError


class Operator(str, Enum):
    EQUALS = auto()
    """x == value"""
    NOT_EQUALS = auto()
    """x != value"""

    GREATER_THAN = auto()
    """x > value"""
    LESS_THAN = auto()
    """x < value"""
    GREATER_THAN_OR_EQUAL = auto()
    """x >= value"""
    LESS_THAN_OR_EQUAL = auto()
    """x <= value"""

    IS_EMPTY = auto()
    """x == ''"""
    IS_NOT_EMPTY = auto()
    """x != ''"""

    IN = auto()
    """x in [value1, value2, ...]"""
    NOT_IN = auto()
    """x not in [value1, value2, ...]"""

    STARTS_WITH = auto()
    """x.startswith('value')"""
    ENDS_WITH = auto()
    """x.endswith('value')"""
    CONTAINS = auto()
    """x.contains('value')"""

    BETWEEN = auto()
    """x.between(value1, value2)"""


class LogicalOperator(str, Enum):
    AND = auto()
    OR = auto()


@immutable
class WhereClause(ValueObject, Generic[AnyT]):
    operator: Operator
    column: str
    value: AnyT | list[AnyT] | tuple[AnyT, AnyT] | None = field(default=None)
    aggregate_with: LogicalOperator = field(default=LogicalOperator.AND)

    def validate(self) -> None:
        super().validate()
        match self.operator:
            case Operator.EQUALS | Operator.NOT_EQUALS:
                if isinstance(self.value, (list, tuple)):
                    raise InvalidWhereClauseError("values must be a single value")
                if isinstance(self.value, IEquatable):
                    raise InvalidWhereClauseError("values must not be equatable")
            case Operator.IN | Operator.NOT_IN:
                if not isinstance(self.value, list):
                    raise InvalidWhereClauseError("values must be a list")
            case Operator.BETWEEN:
                if not isinstance(self.value, tuple):
                    raise InvalidWhereClauseError("values must be a tuple")
            case Operator.IS_EMPTY | Operator.IS_NOT_EMPTY:
                if self.value is not None:
                    raise InvalidWhereClauseError("values must be None")
            case Operator.STARTS_WITH | Operator.ENDS_WITH:
                if isinstance(self.value, (list, tuple)):
                    raise InvalidWhereClauseError("values must be a single value")
                if not isinstance(self.value, str):
                    raise InvalidWhereClauseError("values must be a string")
            case Operator.CONTAINS:
                if isinstance(self.value, (list, tuple)):
                    raise InvalidWhereClauseError("values must be a single value")
                if isinstance(self.value, IEquatable):
                    raise InvalidWhereClauseError("values must not be equatable")
            case (
                Operator.GREATER_THAN
                | Operator.LESS_THAN
                | Operator.GREATER_THAN_OR_EQUAL
                | Operator.LESS_THAN_OR_EQUAL
            ):
                if isinstance(self.value, (list, tuple)):
                    raise InvalidWhereClauseError("values must be a single value")
                if not isinstance(self.value, IComparable):
                    raise InvalidWhereClauseError("values must be comparable")


@immutable
class Where(ValueObject):
    clauses: list[WhereClause[Any]]
