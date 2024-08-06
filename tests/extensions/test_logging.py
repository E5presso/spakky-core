import logging
from logging import Logger, Formatter, LogRecord

import pytest

from spakky.aop.aspect import Aspect, AsyncAspect
from spakky.extensions.logging import AsyncLoggingAdvisor, Logging, LoggingAdvisor


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

    advisor = LoggingAdvisor(logger)
    assert (
        advisor.around(
            joinpoint=Dummy().authenticate,
            username="John",
            password="1234",
        )
        is True
    )
    assert (
        advisor.around(
            Dummy().authenticate,
            "John",
            "12345",
        )
        is False
    )
    with pytest.raises(ValueError, match="Mike?"):
        assert advisor.around(Dummy().authenticate, "Mike", "1234") is False

    assert console.log_records[0].startswith(
        "[INFO]: [LoggingAdvisor] test_logging_with_masking.<locals>.Dummy.authenticate(username='John', password='******') -> True"
    )
    assert console.log_records[1].startswith(
        "[INFO]: [LoggingAdvisor] test_logging_with_masking.<locals>.Dummy.authenticate('John', '12345') -> False"
    )
    assert console.log_records[2].startswith(
        "[ERROR]: [LoggingAdvisor] test_logging_with_masking.<locals>.Dummy.authenticate('Mike', '1234') raised ValueError"
    )
    assert Aspect.single(advisor).matches(Dummy) is True
    assert Aspect.single(advisor).matches(Unmatched) is False


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

    advisor = LoggingAdvisor(logger)
    assert (
        advisor.around(
            joinpoint=Dummy().authenticate,
            username="John",
            password="1234",
        )
        is True
    )
    assert (
        advisor.around(
            Dummy().authenticate,
            "John",
            "12345",
        )
        is False
    )
    with pytest.raises(ValueError, match="Mike?"):
        assert advisor.around(Dummy().authenticate, "Mike", "1234") is False

    assert console.log_records[0].startswith(
        "[INFO]: [LoggingAdvisor] test_logging_without_masking.<locals>.Dummy.authenticate(username='John', password='1234') -> True"
    )
    assert console.log_records[1].startswith(
        "[INFO]: [LoggingAdvisor] test_logging_without_masking.<locals>.Dummy.authenticate('John', '12345') -> False"
    )
    assert console.log_records[2].startswith(
        "[ERROR]: [LoggingAdvisor] test_logging_without_masking.<locals>.Dummy.authenticate('Mike', '1234') raised ValueError"
    )
    assert Aspect.single(advisor).matches(Dummy) is True
    assert Aspect.single(advisor).matches(Unmatched) is False


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

    advisor = AsyncLoggingAdvisor(logger)
    assert (
        await advisor.around_async(
            joinpoint=Dummy().authenticate,
            username="John",
            password="1234",
        )
        is True
    )
    assert (
        await advisor.around_async(
            Dummy().authenticate,
            "John",
            "12345",
        )
        is False
    )
    with pytest.raises(ValueError, match="Mike?"):
        assert await advisor.around_async(Dummy().authenticate, "Mike", "1234") is False

    assert console.log_records[0].startswith(
        "[INFO]: [AsyncLoggingAdvisor] test_async_logging_with_masking.<locals>.Dummy.authenticate(username='John', password='******') -> True"
    )
    assert console.log_records[1].startswith(
        "[INFO]: [AsyncLoggingAdvisor] test_async_logging_with_masking.<locals>.Dummy.authenticate('John', '12345') -> False"
    )
    assert console.log_records[2].startswith(
        "[ERROR]: [AsyncLoggingAdvisor] test_async_logging_with_masking.<locals>.Dummy.authenticate('Mike', '1234') raised ValueError"
    )
    assert AsyncAspect.single(advisor).matches(Dummy) is True
    assert AsyncAspect.single(advisor).matches(Unmatched) is False


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

    advisor = AsyncLoggingAdvisor(logger)
    assert (
        await advisor.around_async(
            joinpoint=Dummy().authenticate,
            username="John",
            password="1234",
        )
        is True
    )
    assert (
        await advisor.around_async(
            Dummy().authenticate,
            "John",
            "12345",
        )
        is False
    )
    with pytest.raises(ValueError, match="Mike?"):
        assert await advisor.around_async(Dummy().authenticate, "Mike", "1234") is False

    assert console.log_records[0].startswith(
        "[INFO]: [AsyncLoggingAdvisor] test_async_logging_without_masking.<locals>.Dummy.authenticate(username='John', password='1234') -> True"
    )
    assert console.log_records[1].startswith(
        "[INFO]: [AsyncLoggingAdvisor] test_async_logging_without_masking.<locals>.Dummy.authenticate('John', '12345') -> False"
    )
    assert console.log_records[2].startswith(
        "[ERROR]: [AsyncLoggingAdvisor] test_async_logging_without_masking.<locals>.Dummy.authenticate('Mike', '1234') raised ValueError"
    )
    assert AsyncAspect.single(advisor).matches(Dummy) is True
    assert AsyncAspect.single(advisor).matches(Unmatched) is False
