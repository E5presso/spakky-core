from typing import Any, Generator

import pytest
from fastapi.testclient import TestClient

from sample.app import app, context
from spakky.dependency.application_context import ApplicationContext


@pytest.fixture(name="context", scope="function")
def context_fixture() -> Generator[ApplicationContext, Any, None]:
    yield context


@pytest.fixture(name="test_client", scope="function")
def test_client_fixture() -> Generator[TestClient, Any, None]:
    with TestClient(app, base_url="http://pytest") as client:
        yield client
