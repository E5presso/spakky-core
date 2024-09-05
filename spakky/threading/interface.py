from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class IManagedThread(Protocol):
    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...
