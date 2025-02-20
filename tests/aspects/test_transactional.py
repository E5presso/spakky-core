import logging
from logging import Formatter, Handler, Logger, LogRecord
from typing import Any

import pytest

from spakky.aop.aspect import Aspect, AsyncAspect
from spakky.aspects.transactional import (
    AsyncTransactionalAspect,
    Transactional,
    TransactionalAspect,
)
from spakky.domain.models.aggregate_root import AbstractAggregateRoot
from spakky.domain.ports.persistency.transaction import (
    AbstractAsyncTransaction,
    AbstractTransaction,
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

        def add(self, aggregate: AbstractAggregateRoot[Any]) -> None: ...

        def delete(self, aggregate: AbstractAggregateRoot[Any]) -> None: ...

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

    aspect = TransactionalAspect(InMemoryTransaction(), logger)
    assert (
        aspect.around(
            Dummy().authenticate,
            username="John",
            password="1234",
        )
        is True
    )

    assert Aspect.get(aspect).matches(Dummy) is True
    assert Aspect.get(aspect).matches(Unmatched) is False


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

        def add(self, aggregate: AbstractAggregateRoot[Any]) -> None: ...

        def delete(self, aggregate: AbstractAggregateRoot[Any]) -> None: ...

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

    aspect = TransactionalAspect(InMemoryTransaction(), logger)
    with pytest.raises(ValueError, match="Mike?"):
        assert aspect.around(
            Dummy().authenticate,
            "Mike",
            "1234",
        )

    assert Aspect.get(aspect).matches(Dummy) is True
    assert Aspect.get(aspect).matches(Unmatched) is False


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

        async def add(self, aggregate: AbstractAggregateRoot[Any]) -> None: ...

        async def delete(self, aggregate: AbstractAggregateRoot[Any]) -> None: ...

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

    aspect = AsyncTransactionalAspect(InMemoryTransaction(), logger)
    assert (
        await aspect.around_async(
            Dummy().authenticate,
            username="John",
            password="1234",
        )
        is True
    )
    assert AsyncAspect.get(aspect).matches(Dummy) is True
    assert AsyncAspect.get(aspect).matches(Unmatched) is False


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

        async def add(self, aggregate: AbstractAggregateRoot[Any]) -> None: ...

        async def delete(self, aggregate: AbstractAggregateRoot[Any]) -> None: ...

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

    aspect = AsyncTransactionalAspect(InMemoryTransaction(), logger)
    with pytest.raises(ValueError, match="Mike?"):
        assert await aspect.around_async(
            Dummy().authenticate,
            "Mike",
            "1234",
        )
    assert AsyncAspect.get(aspect).matches(Dummy) is True
    assert AsyncAspect.get(aspect).matches(Unmatched) is False
