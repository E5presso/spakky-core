from uuid import UUID

import pytest

from sample.adapters.event_publisher import AsyncMemoryEventPublisher
from sample.user.domain.interface.service.command.user_registration import (
    UserRegistrationRequest,
)
from sample.user.domain.model.user import EmailValidationFailedError, User
from sample.user.domain.usecase.command.user_registration import (
    AsyncUserRegistrationUseCase,
)
from sample.user.repository.user import AsyncMemoryUserRepository
from spakky.dependency.application_context import ApplicationContext


@pytest.mark.asyncio
async def test_user_registration(context: ApplicationContext) -> None:
    service = context.get(required_type=AsyncUserRegistrationUseCase)
    uid: UUID = await service.execute(
        UserRegistrationRequest(
            username="testuser",
            password="password",
            email="test@email.com",
        )
    )

    repository = context.get(required_type=AsyncMemoryUserRepository)
    event_publisher = context.get(required_type=AsyncMemoryEventPublisher)
    saved = repository.database[uid]
    assert saved.username == "testuser"
    assert saved.password != "password"
    assert saved.email == "test@email.com"
    assert isinstance(event_publisher.events[0], User.Created)


@pytest.mark.asyncio
async def test_user_registration_expect_email_validation_failed_error(
    context: ApplicationContext,
) -> None:
    service = context.get(required_type=AsyncUserRegistrationUseCase)
    with pytest.raises(EmailValidationFailedError):
        await service.execute(
            UserRegistrationRequest(
                username="testuser",
                password="password",
                email="wrong_email",
            )
        )
