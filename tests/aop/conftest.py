import logging
from typing import Any, Generator
from logging import Logger, Formatter, StreamHandler, getLogger

import pytest

from spakky.aop.post_processor import AspectPostProcessor
from spakky.application.application_context import ApplicationContext
from spakky.aspects.logging import AsyncLoggingAspect, LoggingAspect
from spakky.core.importing import list_objects
from spakky.pod.annotations.pod import Pod
from spakky.security.key import Key
from tests.aop.apps import dummy


@pytest.fixture(name="application_context", scope="function")
def get_application_context_fixture() -> Generator[ApplicationContext, Any, None]:
    console = StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(Formatter("[%(levelname)s] (%(asctime)s) : %(message)s"))

    logger: Logger = getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    @Pod()
    def get_key() -> Key:
        return Key(size=32)

    @Pod()
    def get_logger() -> Logger:
        return logger

    context: ApplicationContext = ApplicationContext()
    context.add(get_key)
    context.add(get_logger)
    context.add(AspectPostProcessor)
    context.add(LoggingAspect)
    context.add(AsyncLoggingAspect)
    for obj in list_objects(dummy, Pod.exists):
        context.add(obj)
    context.start()

    yield context

    logger.handlers.clear()
