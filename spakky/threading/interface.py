from abc import abstractmethod
from typing import Protocol, runtime_checkable
from asyncio import Lock as AsyncLock, Event as AsyncEvent
from threading import Lock as ThreadLock, Event as ThreadEvent


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
