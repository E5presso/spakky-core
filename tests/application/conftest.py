import logging
from logging import Formatter, StreamHandler, getLogger
from typing import Any, Generator

import pytest

from spakky.application.application import SpakkyApplication
from spakky.application.application_context import ApplicationContext
from tests.application import apps


@pytest.fixture(name="application", scope="function")
def application_fixture() -> Generator[SpakkyApplication, Any, None]:
    console = StreamHandler()
    console.setFormatter(Formatter("[%(asctime)s] [%(levelname)s] > %(message)s"))

    logger = getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    app: SpakkyApplication = (
        SpakkyApplication(ApplicationContext(logger=logger))
        .enable_transactional()
        .enable_logging()
        .scan(apps)
        .load_plugins()
        .start()
    )
    yield app
    app.stop()
