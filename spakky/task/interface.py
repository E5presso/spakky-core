from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class ITask(Protocol):
    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...
