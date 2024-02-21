from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from spakky.core.mutability import immutable


@immutable
class Query(ABC):
    ...


QueryT = TypeVar("QueryT", bound=Query)
ResultT = TypeVar("ResultT", bound=Any)


class IQueryUseCase(Generic[QueryT, ResultT], ABC):
    @abstractmethod
    def execute(self, query: QueryT) -> ResultT:
        ...


class IAsyncQueryUseCase(Generic[QueryT, ResultT], ABC):
    @abstractmethod
    async def execute(self, query: QueryT) -> ResultT:
        ...
