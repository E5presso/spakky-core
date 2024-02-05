from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self, final

from spakky.core.interfaces.disposable import IAsyncDisposable, IDisposable


class AbstractUnitOfWork(IDisposable, ABC):
    __autocommit_enabled: bool

    def __init__(self, autocommit: bool = True) -> None:
        self.__autocommit_enabled = autocommit

    @final
    def __enter__(self) -> Self:
        self.initialize()
        return self

    @final
    def __exit__(
        self,
        __exc_type: type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> bool | None:
        if __exc_value is not None:
            self.rollback()
        elif self.__autocommit_enabled:
            self.commit()
        self.dispose()

    @abstractmethod
    def initialize(self) -> None:
        ...

    @abstractmethod
    def dispose(self) -> None:
        ...

    @abstractmethod
    def commit(self) -> None:
        ...

    @abstractmethod
    def rollback(self) -> None:
        ...


class AbstractAsyncUnitOfWork(IAsyncDisposable, ABC):
    __autocommit_enabled: bool

    def __init__(self, autocommit: bool = True) -> None:
        self.__autocommit_enabled = autocommit

    @final
    async def __aenter__(self) -> Self:
        await self.initialize()
        return self

    @final
    async def __aexit__(
        self,
        __exc_type: type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> bool | None:
        if __exc_value is not None:
            await self.rollback()
        elif self.__autocommit_enabled:
            await self.commit()
        await self.dispose()

    @abstractmethod
    async def initialize(self) -> None:
        ...

    @abstractmethod
    async def dispose(self) -> None:
        ...

    @abstractmethod
    async def commit(self) -> None:
        ...

    @abstractmethod
    async def rollback(self) -> None:
        ...
