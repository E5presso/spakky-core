from abc import ABC, abstractmethod
from typing import Any, Protocol, TypeVar, runtime_checkable

from spakky.core.mutability import immutable


@immutable
class Query(ABC): ...


QueryT_contra = TypeVar("QueryT_contra", bound=Query, contravariant=True)
ResultT_co = TypeVar("ResultT_co", bound=Any, covariant=True)


@runtime_checkable
class IQueryUseCase(Protocol[QueryT_contra, ResultT_co]):
    @abstractmethod
    def execute(self, query: QueryT_contra) -> ResultT_co: ...


@runtime_checkable
class IAsyncQueryUseCase(Protocol[QueryT_contra, ResultT_co]):
    @abstractmethod
    async def execute(self, query: QueryT_contra) -> ResultT_co: ...
