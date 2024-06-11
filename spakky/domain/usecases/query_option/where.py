from enum import Enum
from typing import Any, Sequence
from dataclasses import field

from spakky.core.mutability import immutable
from spakky.domain.models.value_object import ValueObject


class Operator(str, Enum):
    EQUALS = "="
    """x `==` value"""
    NOT_EQUALS = "!="
    """x `!=` value"""
    GREATER_THAN = ">"
    """x `>` value"""
    LESS_THAN = "<"
    """x `<` value"""
    GREATER_THAN_OR_EQUAL = ">="
    """x `>=` value"""
    LESS_THAN_OR_EQUAL = "<="
    """x `<=` value"""

    IN = "in"
    """x `in` [value1, value2, ...]"""
    NOT_IN = "not_in"
    """x `not in` [value1, value2, ...]"""
    STARTS_WITH = "starts_with"
    """x `like` 'value%'"""
    ENDS_WITH = "ends_with"
    """x `like` '%value'"""
    CONTAINS = "contains"
    """x `like` '%value%'"""

    IS_EMPTY = "is_empty"
    """x `==` ''"""
    IS_NOT_EMPTY = "is_not_empty"
    """x `!=` ''"""

    BETWEEN = "between"
    """x `between` value1 `and` value2"""


class LogicalOperator(str, Enum):
    AND = "and"
    OR = "or"


@immutable
class WhereClause(ValueObject):
    field: str
    operator: Operator
    values: Sequence[Any]
    logical_operator: LogicalOperator = LogicalOperator.AND


@immutable
class Where(ValueObject):
    clauses: Sequence[WhereClause] = field(default_factory=list[WhereClause])
