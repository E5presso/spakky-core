import logging
from typing import Any, Generator
from logging import Logger, Formatter, StreamHandler, getLogger

import pytest

from spakky.aop.post_processor import AspectPostProcessor
from spakky.application.application_context import ApplicationContext
from spakky.aspects.logging import AsyncLoggingAspect, LoggingAspect
from spakky.core.importing import list_objects
from spakky.pod.pod import Pod
from spakky.security.key import Key
from tests.aop.apps import dummy


@pytest.fixture(name="key", scope="package")
def get_key_fixture() -> Generator[Key, Any, None]:
    key: Key = Key(size=32)
    yield key


@pytest.fixture(name="logger", scope="package")
def get_logger_fixture() -> Generator[Logger, Any, None]:
    console = StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(Formatter("[%(levelname)s] (%(asctime)s) : %(message)s"))

    logger: Logger = getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    yield logger

    logger.removeHandler(console)


@pytest.fixture(name="application_context", scope="function")
def get_application_context_fixture(
    key: Key, logger: Logger
) -> Generator[ApplicationContext, Any, None]:
    @Pod()
    def get_logger() -> Logger:
        return logger

    @Pod()
    def get_key() -> Key:
        return key

    context: ApplicationContext = ApplicationContext()
    context.add(get_logger)
    context.add(get_key)
    context.add(AspectPostProcessor)
    context.add(LoggingAspect)
    context.add(AsyncLoggingAspect)
    for obj in list_objects(dummy, Pod.exists):
        context.add(obj)
    context.start()
    yield context
