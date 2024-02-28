from abc import ABC, abstractmethod
from typing import Any, TypeVar, Protocol, runtime_checkable

from spakky.core.mutability import immutable


@immutable
class Command(ABC):
    ...


CommandT_contra = TypeVar("CommandT_contra", bound=Command, contravariant=True)
ResultT_co = TypeVar("ResultT_co", bound=Any, covariant=True)


@runtime_checkable
class ICommandUseCase(Protocol[CommandT_contra, ResultT_co]):
    @abstractmethod
    def execute(self, command: CommandT_contra) -> ResultT_co:
        ...


@runtime_checkable
class IAsyncCommandUseCase(Protocol[CommandT_contra, ResultT_co]):
    @abstractmethod
    async def execute(self, command: CommandT_contra) -> ResultT_co:
        ...
