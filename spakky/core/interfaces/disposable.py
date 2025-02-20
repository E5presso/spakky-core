import sys
from abc import abstractmethod
from types import TracebackType
from typing import Protocol, TypeVar, runtime_checkable

if sys.version_info >= (3, 11):
    from typing import Self  # pragma: no cover
else:
    from typing_extensions import Self  # pragma: no cover


@runtime_checkable
class IDisposable(Protocol):
    @abstractmethod
    def __enter__(self) -> Self: ...

    @abstractmethod
    def __exit__(
        self,
        __exc_type: type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> bool | None: ...


@runtime_checkable
class IAsyncDisposable(Protocol):
    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(
        self,
        __exc_type: type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> bool | None: ...


DisposableT = TypeVar("DisposableT", bound=IDisposable)
AsyncDisposableT = TypeVar("AsyncDisposableT", bound=IAsyncDisposable)
