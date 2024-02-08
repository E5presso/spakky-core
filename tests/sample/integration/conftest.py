from typing import Any, Generator

import pytest

from sample.app import context
from spakky.dependency.application_context import ApplicationContext


@pytest.fixture(name="context", scope="function")
def context_fixture() -> Generator[ApplicationContext, Any, None]:
    yield context
