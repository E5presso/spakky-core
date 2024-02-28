import logging
from logging import Logger, Formatter, LogRecord

import pytest

from spakky.aspects.logging import AsyncLogging, AsyncLoggingAdvice


@pytest.mark.asyncio
async def test_logging_with_masking() -> None:
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

    @AsyncLogging()
    async def authenticate(username: str, password: str) -> bool:
        if username == "Mike":
            raise ValueError("Mike?")
        return username == "John" and password == "1234"

    advice = AsyncLoggingAdvice(logger)
    assert (
        await advice.around(
            joinpoint=authenticate,
            username="John",
            password="1234",
        )
        is True
    )
    assert (
        await advice.around(
            authenticate,
            "John",
            "12345",
        )
        is False
    )
    with pytest.raises(ValueError, match="Mike?"):
        assert await advice.around(authenticate, "Mike", "1234") is False

    assert console.log_records == [
        "[INFO]: [Log] test_logging_with_masking.<locals>.authenticate(username='John', password='******')",
        "[INFO]: [Log] test_logging_with_masking.<locals>.authenticate(username='John', password='******') -> True",
        "[INFO]: [Log] test_logging_with_masking.<locals>.authenticate('John', '12345')",
        "[INFO]: [Log] test_logging_with_masking.<locals>.authenticate('John', '12345') -> False",
        "[INFO]: [Log] test_logging_with_masking.<locals>.authenticate('Mike', '1234')",
        "[ERROR]: [Log] test_logging_with_masking.<locals>.authenticate('Mike', '1234') raised ValueError",
    ]


async def test_logging_without_masking() -> None:
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

    @AsyncLogging(enable_masking=False)
    async def authenticate(username: str, password: str) -> bool:
        if username == "Mike":
            raise ValueError("Mike?")
        return username == "John" and password == "1234"

    advice = AsyncLoggingAdvice(logger)
    assert (
        await advice.around(
            joinpoint=authenticate,
            username="John",
            password="1234",
        )
        is True
    )
    assert (
        await advice.around(
            authenticate,
            "John",
            "12345",
        )
        is False
    )
    with pytest.raises(ValueError, match="Mike?"):
        assert await advice.around(authenticate, "Mike", "1234") is False

    assert console.log_records == [
        "[INFO]: [Log] test_logging_without_masking.<locals>.authenticate(username='John', password='1234')",
        "[INFO]: [Log] test_logging_without_masking.<locals>.authenticate(username='John', password='1234') -> True",
        "[INFO]: [Log] test_logging_without_masking.<locals>.authenticate('John', '12345')",
        "[INFO]: [Log] test_logging_without_masking.<locals>.authenticate('John', '12345') -> False",
        "[INFO]: [Log] test_logging_without_masking.<locals>.authenticate('Mike', '1234')",
        "[ERROR]: [Log] test_logging_without_masking.<locals>.authenticate('Mike', '1234') raised ValueError",
    ]