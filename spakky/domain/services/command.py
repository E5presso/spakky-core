from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from spakky.core.mutability import immutable


@immutable
class Command(ABC):
    ...


CommandT = TypeVar("CommandT", bound=Command)


class ICommandService(Generic[CommandT], ABC):
    @abstractmethod
    def execute(self, command: CommandT) -> None:
        ...


class IAsyncCommandService(Generic[CommandT], ABC):
    @abstractmethod
    async def execute(self, command: CommandT) -> None:
        ...
