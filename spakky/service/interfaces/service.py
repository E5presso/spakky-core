from abc import abstractmethod
from asyncio import locks
from threading import Event
from typing import Protocol, runtime_checkable


@runtime_checkable
class IService(Protocol):
    @abstractmethod
    def set_stop_event(self, stop_event: Event) -> None: ...

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...


@runtime_checkable
class IAsyncService(Protocol):
    @abstractmethod
    def set_stop_event(self, stop_event: locks.Event) -> None: ...

    @abstractmethod
    async def start_async(self) -> None: ...

    @abstractmethod
    async def stop_async(self) -> None: ...
