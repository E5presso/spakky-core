from abc import ABC, abstractmethod
from asyncio import locks, tasks
from threading import Event as ThreadEvent
from threading import Thread

from spakky.service.interfaces.service import IAsyncService, IService


class AbstractBackgroundService(IService, ABC):
    _thread: Thread | None
    _stop_event: ThreadEvent

    def set_stop_event(self, stop_event: ThreadEvent) -> None:
        self._stop_event = stop_event

    def start(self) -> None:
        self._stop_event.clear()
        self.initialize()
        self._thread = Thread(target=self.run, daemon=True, name=type(self).__name__)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        self.dispose()

    @abstractmethod
    def initialize(self) -> None: ...

    @abstractmethod
    def dispose(self) -> None: ...

    @abstractmethod
    def run(self) -> None: ...


class AbstractAsyncBackgroundService(IAsyncService, ABC):
    _task: tasks.Task[None] | None
    _stop_event: locks.Event

    def set_stop_event(self, stop_event: locks.Event) -> None:
        self._stop_event = stop_event

    async def start_async(self) -> None:
        self._stop_event.clear()
        await self.initialize_async()
        self._task = tasks.create_task(coro=self.run_async(), name=type(self).__name__)

    async def stop_async(self) -> None:
        self._stop_event.set()
        if self._task:
            await self._task
        await self.dispose_async()

    @abstractmethod
    async def initialize_async(self) -> None: ...

    @abstractmethod
    async def dispose_async(self) -> None: ...

    @abstractmethod
    async def run_async(self) -> None: ...
