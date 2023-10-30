from abc import ABC, abstractmethod
from asyncio import Event
from threading import Event as ThreadEvent


class IDaemonTask(ABC):
    @abstractmethod
    def start(self, signal: ThreadEvent) -> None:
        ...


class IAsyncDaemonTask(ABC):
    @abstractmethod
    async def start(self, signal: Event) -> None:
        ...
