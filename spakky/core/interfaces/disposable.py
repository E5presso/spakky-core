from abc import abstractmethod
from types import TracebackType
from typing import Self, TypeVar, Protocol, runtime_checkable


@runtime_checkable
class IDisposable(Protocol):
    """Interface that can initialize and dispose within scope\n
    This is a protocol to use `with` statement
    """

    @abstractmethod
    def __enter__(self) -> Self:
        ...

    @abstractmethod
    def __exit__(
        self,
        __exc_type: type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> bool | None:
        ...


@runtime_checkable
class IAsyncDisposable(Protocol):
    """Interface that can initialize and dispose within scope\n
    The protocol is for asynchronous manner\n
    This is a protocol to use `async with` statement
    """

    async def __aenter__(self) -> Self:
        ...

    async def __aexit__(
        self,
        __exc_type: type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> bool | None:
        ...


DisposableT = TypeVar("DisposableT", bound=IDisposable)
AsyncDisposableT = TypeVar("AsyncDisposableT", bound=IAsyncDisposable)
