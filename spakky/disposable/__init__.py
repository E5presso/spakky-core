from typing import Self, final
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager, AbstractAsyncContextManager


class IDisposable(AbstractContextManager, ABC):
    @final
    def __enter__(self: Self) -> Self:
        return self.initialize()

    @final
    def __exit__(self, *_) -> None:
        self.dispose()
        return

    @abstractmethod
    def initialize(self: Self) -> Self:
        ...

    @abstractmethod
    def dispose(self) -> None:
        ...


class IAsyncDisposable(AbstractAsyncContextManager, ABC):
    @final
    async def __aenter__(self: Self) -> Self:
        return await self.initialize()

    @final
    async def __aexit__(self, *_) -> None:
        await self.dispose()
        return

    @abstractmethod
    async def initialize(self: Self) -> Self:
        ...

    @abstractmethod
    async def dispose(self) -> None:
        ...
