# pylint: disable=line-too-long

import logging
from logging import Logger, Formatter, LogRecord

import pytest

from spakky.aop.aspect import Aspect, AsyncAspect
from spakky.aspects.logging import AsyncLoggingAspect, Logging, LoggingAspect


def test_logging_with_masking() -> None:
    class InMemoryHandler(logging.Handler):
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
        @Logging()
        def authenticate(self, username: str, password: str) -> bool:
            if username == "Mike":
                raise ValueError("Mike?")
            return username == "John" and password == "1234"

    class Unmatched:
        def none(self) -> None:
            pass

    aspect = LoggingAspect(logger)
    assert (
        aspect.around(
            joinpoint=Dummy().authenticate,
            username="John",
            password="1234",
        )
        is True
    )
    assert (
        aspect.around(
            Dummy().authenticate,
            "John",
            "12345",
        )
        is False
    )
    with pytest.raises(ValueError, match="Mike?"):
        assert aspect.around(Dummy().authenticate, "Mike", "1234") is False

    assert console.log_records[0].startswith(
        "[INFO]: [LoggingAspect] test_logging_with_masking.<locals>.Dummy.authenticate(username='John', password='******') -> True"
    )
    assert console.log_records[1].startswith(
        "[INFO]: [LoggingAspect] test_logging_with_masking.<locals>.Dummy.authenticate('John', '12345') -> False"
    )
    assert console.log_records[2].startswith(
        "[ERROR]: [LoggingAspect] test_logging_with_masking.<locals>.Dummy.authenticate('Mike', '1234') raised ValueError"
    )
    assert Aspect.get(aspect).matches(Dummy) is True
    assert Aspect.get(aspect).matches(Unmatched) is False


def test_logging_without_masking() -> None:
    class InMemoryHandler(logging.Handler):
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
        @Logging(enable_masking=False)
        def authenticate(self, username: str, password: str) -> bool:
            if username == "Mike":
                raise ValueError("Mike?")
            return username == "John" and password == "1234"

    class Unmatched:
        def none(self) -> None:
            pass

    aspect = LoggingAspect(logger)
    assert (
        aspect.around(
            joinpoint=Dummy().authenticate,
            username="John",
            password="1234",
        )
        is True
    )
    assert (
        aspect.around(
            Dummy().authenticate,
            "John",
            "12345",
        )
        is False
    )
    with pytest.raises(ValueError, match="Mike?"):
        assert aspect.around(Dummy().authenticate, "Mike", "1234") is False

    assert console.log_records[0].startswith(
        "[INFO]: [LoggingAspect] test_logging_without_masking.<locals>.Dummy.authenticate(username='John', password='1234') -> True"
    )
    assert console.log_records[1].startswith(
        "[INFO]: [LoggingAspect] test_logging_without_masking.<locals>.Dummy.authenticate('John', '12345') -> False"
    )
    assert console.log_records[2].startswith(
        "[ERROR]: [LoggingAspect] test_logging_without_masking.<locals>.Dummy.authenticate('Mike', '1234') raised ValueError"
    )
    assert Aspect.get(aspect).matches(Dummy) is True
    assert Aspect.get(aspect).matches(Unmatched) is False


@pytest.mark.asyncio
async def test_async_logging_with_masking() -> None:
    class InMemoryHandler(logging.Handler):
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
        @Logging()
        async def authenticate(self, username: str, password: str) -> bool:
            if username == "Mike":
                raise ValueError("Mike?")
            return username == "John" and password == "1234"

    class Unmatched:
        async def none(self) -> None:
            pass

    aspect = AsyncLoggingAspect(logger)
    assert (
        await aspect.around_async(
            joinpoint=Dummy().authenticate,
            username="John",
            password="1234",
        )
        is True
    )
    assert (
        await aspect.around_async(
            Dummy().authenticate,
            "John",
            "12345",
        )
        is False
    )
    with pytest.raises(ValueError, match="Mike?"):
        assert await aspect.around_async(Dummy().authenticate, "Mike", "1234") is False

    assert console.log_records[0].startswith(
        "[INFO]: [AsyncLoggingAspect] test_async_logging_with_masking.<locals>.Dummy.authenticate(username='John', password='******') -> True"
    )
    assert console.log_records[1].startswith(
        "[INFO]: [AsyncLoggingAspect] test_async_logging_with_masking.<locals>.Dummy.authenticate('John', '12345') -> False"
    )
    assert console.log_records[2].startswith(
        "[ERROR]: [AsyncLoggingAspect] test_async_logging_with_masking.<locals>.Dummy.authenticate('Mike', '1234') raised ValueError"
    )
    assert AsyncAspect.get(aspect).matches(Dummy) is True
    assert AsyncAspect.get(aspect).matches(Unmatched) is False


@pytest.mark.asyncio
async def test_async_logging_without_masking() -> None:
    class InMemoryHandler(logging.Handler):
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
        @Logging(enable_masking=False)
        async def authenticate(self, username: str, password: str) -> bool:
            if username == "Mike":
                raise ValueError("Mike?")
            return username == "John" and password == "1234"

    class Unmatched:
        async def none(self) -> None:
            pass

    aspect = AsyncLoggingAspect(logger)
    assert (
        await aspect.around_async(
            joinpoint=Dummy().authenticate,
            username="John",
            password="1234",
        )
        is True
    )
    assert (
        await aspect.around_async(
            Dummy().authenticate,
            "John",
            "12345",
        )
        is False
    )
    with pytest.raises(ValueError, match="Mike?"):
        assert await aspect.around_async(Dummy().authenticate, "Mike", "1234") is False

    assert console.log_records[0].startswith(
        "[INFO]: [AsyncLoggingAspect] test_async_logging_without_masking.<locals>.Dummy.authenticate(username='John', password='1234') -> True"
    )
    assert console.log_records[1].startswith(
        "[INFO]: [AsyncLoggingAspect] test_async_logging_without_masking.<locals>.Dummy.authenticate('John', '12345') -> False"
    )
    assert console.log_records[2].startswith(
        "[ERROR]: [AsyncLoggingAspect] test_async_logging_without_masking.<locals>.Dummy.authenticate('Mike', '1234') raised ValueError"
    )
    assert AsyncAspect.get(aspect).matches(Dummy) is True
    assert AsyncAspect.get(aspect).matches(Unmatched) is False
