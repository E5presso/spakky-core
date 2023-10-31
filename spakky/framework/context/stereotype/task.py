from abc import abstractmethod
from dataclasses import dataclass
from threading import Event as ThreadEvent
from typing import Protocol, runtime_checkable

from spakky.framework.context.stereotype.component import Component


@runtime_checkable
class ISyncTask(Protocol):
    @abstractmethod
    def start(self, signal: ThreadEvent) -> None:
        ...


@dataclass
class SyncTask(Component):
    ...
