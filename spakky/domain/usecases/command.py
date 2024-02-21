from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from spakky.core.mutability import immutable


@immutable
class Command(ABC):
    ...


CommandT = TypeVar("CommandT", bound=Command)
ResultT = TypeVar("ResultT", bound=Any)


class ICommandUseCase(Generic[CommandT, ResultT], ABC):
    @abstractmethod
    def execute(self, command: CommandT) -> ResultT:
        ...


class IAsyncCommandUseCase(Generic[CommandT, ResultT], ABC):
    @abstractmethod
    async def execute(self, command: CommandT) -> ResultT:
        ...
