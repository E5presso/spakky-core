from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from sample.apps.user.domain.model.user import User
from sample.apps.user.repository.user import AsyncInMemoryUserRepository
from spakky.dependency.application_context import ApplicationContext


@pytest.mark.asyncio
async def test_user_registration_expect_email_validation_failed_error(
    test_client: TestClient,
) -> None:
    response: Response = test_client.post(
        url="/users/v1",
        json={
            "username": "testuser",
            "password": "pa55word!!",
            "email": "wrong_email_format",
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.decode() == "유효하지 않은 이메일 형식입니다."


@pytest.mark.asyncio
async def test_user_registration_expect_user_already_exists_error(
    context: ApplicationContext, test_client: TestClient
) -> None:
    repository = context.get(required_type=AsyncInMemoryUserRepository)
    user = await repository.save(
        User.create(
            username="testuser",
            password="pa55word!!",
            email="test@email.com",
        )
    )
    response: Response = test_client.post(
        url="/users/v1",
        json={
            "username": "testuser",
            "password": "pa55word!!",
            "email": "test@email.com",
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.content.decode() == "이미 존재하는 사용자입니다."
    await repository.delete(user)


@pytest.mark.asyncio
async def test_user_registration_succeed(test_client: TestClient) -> None:
    response: Response = test_client.post(
        url="/users/v1",
        json={
            "username": "testuser",
            "password": "pa55word!!",
            "email": "test@email.com",
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.content.decode() != ""
