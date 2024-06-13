from spakky.domain.error import SpakkyDomainError
from spakky.domain.usecases.criteria.where import Operator


class InvalidWhereClauseError(SpakkyDomainError):
    message = """Invalid where clause. check the operator and values"""

    def __init__(self, reason: str) -> None:
        self.message = (
            f"""Invalid where clause. check the operator and values ({reason})"""
        )


class InvalidColumnError(SpakkyDomainError):
    message = """Invalid column name"""

    def __init__(self, column: str) -> None:
        self.message = f"Invalid column name '{column}'"


class OperationNotSupportedError(SpakkyDomainError):
    message = """Type of given column does not support that operator"""

    def __init__(self, column: str, operator: Operator) -> None:
        self.message = f"Type of '{column}' does not support '{operator.name}' operator"
