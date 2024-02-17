from uuid import UUID

import pytest

from sample.apps.user.domain.interface.usecase.command.user_registration import (
    UserRegistrationRequest,
)
from sample.apps.user.domain.model.user import EmailValidationFailedError, User
from sample.apps.user.domain.usecase.command.user_registration import (
    AsyncUserRegistrationUseCase,
)
from sample.apps.user.repository.user import AsyncInMemoryUserRepository
from sample.common.adapters.event_publisher import AsyncInMemoryEventPublisher
from spakky.dependency.application_context import ApplicationContext


@pytest.mark.asyncio
async def test_user_registration_expect_email_validation_failed_error(
    context: ApplicationContext,
) -> None:
    usecase = context.get(required_type=AsyncUserRegistrationUseCase)
    with pytest.raises(EmailValidationFailedError):
        await usecase.execute(
            UserRegistrationRequest(
                username="testuser",
                password="password",
                email="wrong_email",
            )
        )


@pytest.mark.asyncio
async def test_user_registration_succeed(context: ApplicationContext) -> None:
    usecase = context.get(required_type=AsyncUserRegistrationUseCase)
    uid: UUID = await usecase.execute(
        UserRegistrationRequest(
            username="testuser",
            password="password",
            email="test@email.com",
        )
    )

    repository = context.get(required_type=AsyncInMemoryUserRepository)
    event_publisher = context.get(required_type=AsyncInMemoryEventPublisher)
    saved = repository.database[uid]
    assert saved.username == "testuser"
    assert saved.password != "password"
    assert saved.email == "test@email.com"
    assert isinstance(event_publisher.events[0], User.Created)
