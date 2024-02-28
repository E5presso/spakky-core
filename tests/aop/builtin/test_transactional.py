import logging
from logging import Logger, Handler, Formatter, LogRecord

import pytest

from spakky.aop.builtin.transactional import AsyncTransactionalAdvisor
from spakky.domain.interfaces.transaction import AbstractAsyncTranasction


@pytest.mark.asyncio
async def test_transactional_commit() -> None:
    class InMemoryTransaction(AbstractAsyncTranasction):
        committed: bool
        rolled_back: bool

        def __init__(self, autocommit: bool = True) -> None:
            super().__init__(autocommit)
            self.committed = False
            self.rolled_back = False

        async def initialize(self) -> None:
            self.committed = False
            self.rolled_back = False

        async def dispose(self) -> None:
            return

        async def commit(self) -> None:
            self.committed = True

        async def rollback(self) -> None:
            self.rolled_back = True

    class InMemoryHandler(Handler):
        log_records: list[str]

        def __init__(self) -> None:
            super().__init__()
            self.log_records = []

        def emit(self, record: LogRecord) -> None:
            self.log_records.append(self.format(record))

    console = InMemoryHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(Formatter("[%(levelname)s]: %(message)s"))
    logger: Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    async def authenticate(username: str, password: str) -> bool:
        if username == "Mike":
            raise ValueError("Mike?")
        return username == "John" and password == "1234"

    advice = AsyncTransactionalAdvisor(InMemoryTransaction(), logger)
    assert (
        await advice.around_async(
            authenticate,
            username="John",
            password="1234",
        )
        is True
    )

    assert console.log_records == [
        "[INFO]: [Transaction] BEGIN TRANSACTION",
        "[INFO]: [Transaction] COMMIT",
    ]


@pytest.mark.asyncio
async def test_transactional_rollback() -> None:
    class InMemoryTransaction(AbstractAsyncTranasction):
        committed: bool
        rolled_back: bool

        def __init__(self, autocommit: bool = True) -> None:
            super().__init__(autocommit)
            self.committed = False
            self.rolled_back = False

        async def initialize(self) -> None:
            self.committed = False
            self.rolled_back = False

        async def dispose(self) -> None:
            return

        async def commit(self) -> None:
            self.committed = True

        async def rollback(self) -> None:
            self.rolled_back = True

    class InMemoryHandler(Handler):
        log_records: list[str]

        def __init__(self) -> None:
            super().__init__()
            self.log_records = []

        def emit(self, record: LogRecord) -> None:
            self.log_records.append(self.format(record))

    console = InMemoryHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(Formatter("[%(levelname)s]: %(message)s"))
    logger: Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    async def authenticate(username: str, password: str) -> bool:
        if username == "Mike":
            raise ValueError("Mike?")
        return username == "John" and password == "1234"

    advice = AsyncTransactionalAdvisor(InMemoryTransaction(), logger)
    with pytest.raises(ValueError, match="Mike?"):
        assert await advice.around_async(
            authenticate,
            "Mike",
            "1234",
        )

    assert console.log_records == [
        "[INFO]: [Transaction] BEGIN TRANSACTION",
        "[INFO]: [Transaction] ROLLBACK",
    ]
