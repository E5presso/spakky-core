from abc import abstractmethod
from dataclasses import dataclass
from asyncio import Event
from typing import Protocol, runtime_checkable

from spakky.framework.context.stereotype.component import Component


@runtime_checkable
class IAsyncTask(Protocol):
    @abstractmethod
    async def start(self, signal: Event) -> None:
        ...


@dataclass
class AsyncTask(Component):
    ...
