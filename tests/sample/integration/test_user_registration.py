import pytest

from sample.adapters.event_publisher import AsyncMemoryEventPublisher
from sample.user.domain.interface.service.command.user_registration import (
    UserRegistrationCommand,
)
from sample.user.domain.model.user import User
from sample.user.domain.service.command.user_registration import (
    AsyncUserRegistrationService,
)
from sample.user.repository.user import AsyncMemoryUserRepository
from spakky.dependency.application_context import ApplicationContext


@pytest.mark.asyncio
async def test_user_registration(context: ApplicationContext) -> None:
    repository = context.get(required_type=AsyncMemoryUserRepository)
    event_publisher = context.get(required_type=AsyncMemoryEventPublisher)
    service = context.get(required_type=AsyncUserRegistrationService)
    await service.execute(
        UserRegistrationCommand(
            username="testuser",
            password="password",
            email="test@email.com",
        )
    )

    saved = repository.database[list(repository.database.keys())[0]]
    assert saved.username == "testuser"
    assert saved.password != "password"
    assert saved.email == "test@email.com"
    assert isinstance(event_publisher.events[0], User.Created)
