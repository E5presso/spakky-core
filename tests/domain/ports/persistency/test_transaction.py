import pytest

from spakky.domain.ports.persistency.transaction import (
    AbstractAsyncTranasction,
    AbstractTransaction,
)


def test_tranasction_auto_commit() -> None:
    class InMemoryTransaction(AbstractTransaction):
        committed: bool = False
        rolled_back: bool = False

        def initialize(self) -> None:
            self.committed = False
            self.rolled_back = False

        def dispose(self) -> None: ...

        def commit(self) -> None:
            self.committed = True

        def rollback(self) -> None:
            self.rolled_back = True

    transaction: InMemoryTransaction = InMemoryTransaction(autocommit=True)

    with transaction:
        print("do_something")

    assert transaction.committed is True
    assert transaction.rolled_back is False


def test_tranasction_manual_commit() -> None:
    class InMemoryTransaction(AbstractTransaction):
        committed: bool = False
        rolled_back: bool = False

        def initialize(self) -> None:
            self.committed = False
            self.rolled_back = False

        def dispose(self) -> None: ...

        def commit(self) -> None:
            self.committed = True

        def rollback(self) -> None:
            self.rolled_back = True

    transaction: InMemoryTransaction = InMemoryTransaction(autocommit=False)

    with transaction:
        print("do_something")

    assert transaction.committed is False
    assert transaction.rolled_back is False

    with transaction as tx:
        print("do_something")
        tx.commit()

    assert transaction.committed is True
    assert transaction.rolled_back is False


def test_tranasction_rollback_when_raised() -> None:
    class InMemoryTransaction(AbstractTransaction):
        committed: bool = False
        rolled_back: bool = False

        def initialize(self) -> None:
            self.committed = False
            self.rolled_back = False

        def dispose(self) -> None: ...

        def commit(self) -> None:
            self.committed = True

        def rollback(self) -> None:
            self.rolled_back = True

    transaction: InMemoryTransaction = InMemoryTransaction(autocommit=True)

    with pytest.raises(RuntimeError):
        with transaction:
            raise RuntimeError

    assert transaction.committed is False
    assert transaction.rolled_back is True


@pytest.mark.asyncio
async def test_async_tranasction_auto_commit() -> None:
    class AsyncInMemoryTransaction(AbstractAsyncTranasction):
        committed: bool = False
        rolled_back: bool = False

        async def initialize(self) -> None:
            self.committed = False
            self.rolled_back = False

        async def dispose(self) -> None: ...

        async def commit(self) -> None:
            self.committed = True

        async def rollback(self) -> None:
            self.rolled_back = True

    transaction: AsyncInMemoryTransaction = AsyncInMemoryTransaction(autocommit=True)

    async with transaction:
        print("do_something")

    assert transaction.committed is True
    assert transaction.rolled_back is False


@pytest.mark.asyncio
async def test_async_tranasction_manual_commit() -> None:
    class AsyncInMemoryTransaction(AbstractAsyncTranasction):
        committed: bool = False
        rolled_back: bool = False

        async def initialize(self) -> None:
            self.committed = False
            self.rolled_back = False

        async def dispose(self) -> None: ...

        async def commit(self) -> None:
            self.committed = True

        async def rollback(self) -> None:
            self.rolled_back = True

    transaction: AsyncInMemoryTransaction = AsyncInMemoryTransaction(autocommit=False)

    async with transaction:
        print("do_something")

    assert transaction.committed is False
    assert transaction.rolled_back is False

    async with transaction as tx:
        print("do_something")
        await tx.commit()

    assert transaction.committed is True
    assert transaction.rolled_back is False


@pytest.mark.asyncio
async def test_async_tranasction_rollback_when_raised() -> None:
    class AsyncInMemoryTransaction(AbstractAsyncTranasction):
        committed: bool = False
        rolled_back: bool = False

        async def initialize(self) -> None:
            self.committed = False
            self.rolled_back = False

        async def dispose(self) -> None: ...

        async def commit(self) -> None:
            self.committed = True

        async def rollback(self) -> None:
            self.rolled_back = True

    transaction: AsyncInMemoryTransaction = AsyncInMemoryTransaction(autocommit=True)

    with pytest.raises(RuntimeError):
        async with transaction:
            raise RuntimeError

    assert transaction.committed is False
    assert transaction.rolled_back is True
