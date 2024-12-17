from abc import abstractmethod
from typing import Protocol, runtime_checkable
from threading import Lock as ThreadLock, Event as ThreadEvent
from asyncio.locks import Lock as AsyncLock, Event as AsyncEvent

from spakky.threading.error import SpakkyThreadingError


class ThreadAlreadyStartedError(SpakkyThreadingError):
    message = "Thread is already started"


class ThreadNotStartedError(SpakkyThreadingError):
    message = "Thread is not started"


@runtime_checkable
class IManagedThread(Protocol):
    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...


@runtime_checkable
class IManagedThreadAction(Protocol):
    @abstractmethod
    def __call__(self, event: ThreadEvent, lock: ThreadLock) -> None: ...


@runtime_checkable
class IAsyncManagedThreadAction(Protocol):
    @abstractmethod
    async def __call__(self, event: AsyncEvent, lock: AsyncLock) -> None: ...
