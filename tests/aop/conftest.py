import logging
from typing import Any, Generator
from logging import Logger, Formatter, StreamHandler, getLogger

import pytest

from spakky.aop.post_processor import AspectPostProcessor
from spakky.application.application_context import ApplicationContext
from spakky.aspects.logging import AsyncLoggingAspect, LoggingAspect
from spakky.injectable.injectable import Injectable
from spakky.security.key import Key
from tests.aop import apps
from tests.aop.apps.dummy import AsyncDummyAdvisor, DummyAdvisor


@pytest.fixture(name="key", scope="package")
def get_key_fixture() -> Generator[Key, Any, None]:
    key: Key = Key(size=32)
    yield key


@pytest.fixture(name="logger", scope="package")
def get_logger_fixture() -> Generator[Logger, Any, None]:
    logger: Logger = getLogger("debug")
    logger.setLevel(logging.DEBUG)
    console = StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(Formatter("[%(levelname)s] (%(asctime)s) : %(message)s"))
    logger.addHandler(console)

    yield logger

    logger.removeHandler(console)


@pytest.fixture(name="application_context", scope="function")
def get_application_context_fixture(
    key: Key, logger: Logger
) -> Generator[ApplicationContext, Any, None]:
    @Injectable()
    def get_logger() -> Logger:
        return logger

    @Injectable()
    def get_key() -> Key:
        return key

    context: ApplicationContext = ApplicationContext({apps})
    context.register_injectable(get_logger)
    context.register_injectable(get_key)
    context.register_injectable(DummyAdvisor)
    context.register_injectable(LoggingAspect)
    context.register_injectable(AsyncDummyAdvisor)
    context.register_injectable(AsyncLoggingAspect)
    context.register_post_processor(AspectPostProcessor(logger))
    context.start()
    yield context
