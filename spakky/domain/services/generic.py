from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from spakky.core.mutability import immutable


@immutable
class Request(ABC):
    ...


RequestT = TypeVar("RequestT", bound=Request)
ResponseT = TypeVar("ResponseT", bound=Any)


class IGenericService(Generic[RequestT, ResponseT], ABC):
    @abstractmethod
    def execute(self, request: RequestT) -> ResponseT:
        ...


class IAsyncGenericService(Generic[RequestT, ResponseT], ABC):
    @abstractmethod
    async def execute(self, request: RequestT) -> ResponseT:
        ...
