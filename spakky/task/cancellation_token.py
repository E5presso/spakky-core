from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class ICancellationToken(Protocol):
    @abstractmethod
    def is_set(self) -> bool: ...

    @abstractmethod
    def set(self) -> None: ...

    @abstractmethod
    def clear(self) -> None: ...
