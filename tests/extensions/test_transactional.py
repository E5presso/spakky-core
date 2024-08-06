import logging
from logging import Logger, Handler, Formatter, LogRecord

import pytest

from spakky.aop.aspect import Aspect, AsyncAspect
from spakky.domain.ports.persistency.transaction import (
    AbstractAsyncTransaction,
    AbstractTransaction,
)
from spakky.extensions.transactional import (
    AsyncTransactionalAdvisor,
    Transactional,
    TransactionalAdvisor,
)


def test_transactional_commit() -> None:
    class InMemoryTransaction(AbstractTransaction):
        committed: bool
        rolled_back: bool

        def __init__(self, autocommit: bool = True) -> None:
            super().__init__(autocommit)
            self.committed = False
            self.rolled_back = False

        def initialize(self) -> None:
            self.committed = False
            self.rolled_back = False

        def dispose(self) -> None:
            return

        def commit(self) -> None:
            self.committed = True

        def rollback(self) -> None:
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

    class Dummy:
        @Transactional()
        def authenticate(self, username: str, password: str) -> bool:
            if username == "Mike":
                raise ValueError("Mike?")
            return username == "John" and password == "1234"

    class Unmatched:
        def none(self) -> None:
            pass

    advisor = TransactionalAdvisor(InMemoryTransaction(), logger)
    assert (
        advisor.around(
            Dummy().authenticate,
            username="John",
            password="1234",
        )
        is True
    )

    assert console.log_records == [
        "[INFO]: [TransactionalAdvisor] BEGIN TRANSACTION",
        "[INFO]: [TransactionalAdvisor] COMMIT",
    ]

    assert Aspect.single(advisor).matches(Dummy) is True
    assert Aspect.single(advisor).matches(Unmatched) is False


def test_transactional_rollback() -> None:
    class InMemoryTransaction(AbstractTransaction):
        committed: bool
        rolled_back: bool

        def __init__(self, autocommit: bool = True) -> None:
            super().__init__(autocommit)
            self.committed = False
            self.rolled_back = False

        def initialize(self) -> None:
            self.committed = False
            self.rolled_back = False

        def dispose(self) -> None:
            return

        def commit(self) -> None:
            self.committed = True

        def rollback(self) -> None:
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

    class Dummy:
        @Transactional()
        def authenticate(self, username: str, password: str) -> bool:
            if username == "Mike":
                raise ValueError("Mike?")
            return username == "John" and password == "1234"

    class Unmatched:
        def none(self) -> None:
            pass

    advisor = TransactionalAdvisor(InMemoryTransaction(), logger)
    with pytest.raises(ValueError, match="Mike?"):
        assert advisor.around(
            Dummy().authenticate,
            "Mike",
            "1234",
        )

    assert console.log_records == [
        "[INFO]: [TransactionalAdvisor] BEGIN TRANSACTION",
        "[INFO]: [TransactionalAdvisor] ROLLBACK",
    ]

    assert Aspect.single(advisor).matches(Dummy) is True
    assert Aspect.single(advisor).matches(Unmatched) is False


@pytest.mark.asyncio
async def test_async_transactional_commit() -> None:
    class InMemoryTransaction(AbstractAsyncTransaction):
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

    class Dummy:
        @Transactional()
        async def authenticate(self, username: str, password: str) -> bool:
            if username == "Mike":
                raise ValueError("Mike?")
            return username == "John" and password == "1234"

    class Unmatched:
        async def none(self) -> None:
            pass

    advisor = AsyncTransactionalAdvisor(InMemoryTransaction(), logger)
    assert (
        await advisor.around_async(
            Dummy().authenticate,
            username="John",
            password="1234",
        )
        is True
    )

    assert console.log_records == [
        "[INFO]: [AsyncTransactionalAdvisor] BEGIN TRANSACTION",
        "[INFO]: [AsyncTransactionalAdvisor] COMMIT",
    ]
    assert AsyncAspect.single(advisor).matches(Dummy) is True
    assert AsyncAspect.single(advisor).matches(Unmatched) is False


@pytest.mark.asyncio
async def test_async_transactional_rollback() -> None:
    class InMemoryTransaction(AbstractAsyncTransaction):
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

    class Dummy:
        @Transactional()
        async def authenticate(self, username: str, password: str) -> bool:
            if username == "Mike":
                raise ValueError("Mike?")
            return username == "John" and password == "1234"

    class Unmatched:
        async def none(self) -> None:
            pass

    advisor = AsyncTransactionalAdvisor(InMemoryTransaction(), logger)
    with pytest.raises(ValueError, match="Mike?"):
        assert await advisor.around_async(
            Dummy().authenticate,
            "Mike",
            "1234",
        )

    assert console.log_records == [
        "[INFO]: [AsyncTransactionalAdvisor] BEGIN TRANSACTION",
        "[INFO]: [AsyncTransactionalAdvisor] ROLLBACK",
    ]
    assert AsyncAspect.single(advisor).matches(Dummy) is True
    assert AsyncAspect.single(advisor).matches(Unmatched) is False
