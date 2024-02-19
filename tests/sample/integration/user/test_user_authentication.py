from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from sample.apps.user.domain.model.user import User
from sample.apps.user.repository.user import AsyncInMemoryUserRepository
from spakky.dependency.application_context import ApplicationContext


@pytest.mark.asyncio
async def test_user_authentication_expect_authentication_failed_error(
    test_client: TestClient,
) -> None:
    response: Response = test_client.post(
        "/users/v1/authenticate",
        json={
            "username": "user",
            "password": "password",
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_user_authentication_expect_password_authentication_failed_error(
    context: ApplicationContext, test_client: TestClient
) -> None:
    repository = context.get(required_type=AsyncInMemoryUserRepository)
    await repository.save(
        User.create(
            username="user",
            password="password",
            email="test@email.com",
        )
    )
    response: Response = test_client.post(
        "/users/v1/authenticate",
        json={
            "username": "user",
            "password": "wrong",
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_user_authentication_expect_succeed(
    context: ApplicationContext, test_client: TestClient
) -> None:
    repository = context.get(required_type=AsyncInMemoryUserRepository)
    await repository.save(
        User.create(
            username="user",
            password="password",
            email="test@email.com",
        )
    )
    response: Response = test_client.post(
        "/users/v1/authenticate",
        json={
            "username": "user",
            "password": "password",
        },
    )
    assert response.status_code == HTTPStatus.OK
