import logging
from typing import Any, Generator
from logging import Logger, Formatter, StreamHandler, getLogger

import pytest


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
