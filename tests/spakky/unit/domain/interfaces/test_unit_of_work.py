import pytest

from spakky.domain.interfaces.unit_of_work import (
    AbstractAsyncUnitOfWork,
    AbstractUnitOfWork,
)


def test_unit_of_work_auto_commit() -> None:
    class InMemoryUnitOfWork(AbstractUnitOfWork):
        committed: bool = False
        rolled_back: bool = False

        def initialize(self) -> None:
            self.committed = False
            self.rolled_back = False

        def dispose(self) -> None:
            ...

        def commit(self) -> None:
            self.committed = True

        def rollback(self) -> None:
            self.rolled_back = True

    uow: InMemoryUnitOfWork = InMemoryUnitOfWork(autocommit=True)

    with uow:
        print("do_something")

    assert uow.committed is True
    assert uow.rolled_back is False


def test_unit_of_work_manual_commit() -> None:
    class InMemoryUnitOfWork(AbstractUnitOfWork):
        committed: bool = False
        rolled_back: bool = False

        def initialize(self) -> None:
            self.committed = False
            self.rolled_back = False

        def dispose(self) -> None:
            ...

        def commit(self) -> None:
            self.committed = True

        def rollback(self) -> None:
            self.rolled_back = True

    uow: InMemoryUnitOfWork = InMemoryUnitOfWork(autocommit=False)

    with uow:
        print("do_something")

    assert uow.committed is False
    assert uow.rolled_back is False

    with uow as tx:
        print("do_something")
        tx.commit()

    assert uow.committed is True
    assert uow.rolled_back is False


def test_unit_of_work_rollback_when_raised() -> None:
    class InMemoryUnitOfWork(AbstractUnitOfWork):
        committed: bool = False
        rolled_back: bool = False

        def initialize(self) -> None:
            self.committed = False
            self.rolled_back = False

        def dispose(self) -> None:
            ...

        def commit(self) -> None:
            self.committed = True

        def rollback(self) -> None:
            self.rolled_back = True

    uow: InMemoryUnitOfWork = InMemoryUnitOfWork(autocommit=True)

    with pytest.raises(RuntimeError):
        with uow:
            raise RuntimeError

    assert uow.committed is False
    assert uow.rolled_back is True


@pytest.mark.asyncio
async def test_async_unit_of_work_auto_commit() -> None:
    class AsyncInMemoryUnitOfWork(AbstractAsyncUnitOfWork):
        committed: bool = False
        rolled_back: bool = False

        async def initialize(self) -> None:
            self.committed = False
            self.rolled_back = False

        async def dispose(self) -> None:
            ...

        async def commit(self) -> None:
            self.committed = True

        async def rollback(self) -> None:
            self.rolled_back = True

    uow: AsyncInMemoryUnitOfWork = AsyncInMemoryUnitOfWork(autocommit=True)

    async with uow:
        print("do_something")

    assert uow.committed is True
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_async_unit_of_work_manual_commit() -> None:
    class AsyncInMemoryUnitOfWork(AbstractAsyncUnitOfWork):
        committed: bool = False
        rolled_back: bool = False

        async def initialize(self) -> None:
            self.committed = False
            self.rolled_back = False

        async def dispose(self) -> None:
            ...

        async def commit(self) -> None:
            self.committed = True

        async def rollback(self) -> None:
            self.rolled_back = True

    uow: AsyncInMemoryUnitOfWork = AsyncInMemoryUnitOfWork(autocommit=False)

    async with uow:
        print("do_something")

    assert uow.committed is False
    assert uow.rolled_back is False

    async with uow as tx:
        print("do_something")
        await tx.commit()

    assert uow.committed is True
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_async_unit_of_work_rollback_when_raised() -> None:
    class AsyncInMemoryUnitOfWork(AbstractAsyncUnitOfWork):
        committed: bool = False
        rolled_back: bool = False

        async def initialize(self) -> None:
            self.committed = False
            self.rolled_back = False

        async def dispose(self) -> None:
            ...

        async def commit(self) -> None:
            self.committed = True

        async def rollback(self) -> None:
            self.rolled_back = True

    uow: AsyncInMemoryUnitOfWork = AsyncInMemoryUnitOfWork(autocommit=True)

    with pytest.raises(RuntimeError):
        async with uow:
            raise RuntimeError

    assert uow.committed is False
    assert uow.rolled_back is True
