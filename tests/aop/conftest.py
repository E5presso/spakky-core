import logging
from typing import Any, Generator
from logging import Logger, Formatter, StreamHandler, getLogger

import pytest

from spakky.aop.post_processor import AspectBeanPostProcessor
from spakky.bean.application_context import ApplicationContext
from spakky.bean.bean import BeanFactory
from spakky.cryptography.key import Key
from spakky.extensions.logging import AsyncLoggingAdvisor, LoggingAdvisor
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
    @BeanFactory()
    def get_logger() -> Logger:
        return logger

    @BeanFactory()
    def get_key() -> Key:
        return key

    context: ApplicationContext = ApplicationContext(apps)
    context.register_bean_factory(get_logger)
    context.register_bean_factory(get_key)
    context.register_bean(DummyAdvisor)
    context.register_bean(LoggingAdvisor)
    context.register_bean(AsyncDummyAdvisor)
    context.register_bean(AsyncLoggingAdvisor)
    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.start()
    yield context
