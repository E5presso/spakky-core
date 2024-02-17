import pytest

from sample.apps.user.domain.interface.usecase.command.user_authentication import (
    UserAuthenticationCommand,
)
from sample.apps.user.domain.model.user import AuthenticationFailedError, User
from sample.apps.user.domain.usecase.command.user_authentication import (
    AsyncUserAuthenticationUseCase,
)
from sample.apps.user.repository.user import AsyncInMemoryUserRepository
from spakky.dependency.application_context import ApplicationContext


@pytest.mark.asyncio
async def test_user_authentication_expect_authentication_failed_error(
    context: ApplicationContext,
) -> None:
    usecase = context.get(required_type=AsyncUserAuthenticationUseCase)
    with pytest.raises(AuthenticationFailedError):
        await usecase.execute(
            UserAuthenticationCommand(
                username="user",
                password="password",
            )
        )


@pytest.mark.asyncio
async def test_user_authentication_expect_password_authentication_failed_error(
    context: ApplicationContext,
) -> None:
    repository = context.get(required_type=AsyncInMemoryUserRepository)
    await repository.save(
        User.create(
            username="user",
            password="password",
            email="test@email.com",
        )
    )
    usecase = context.get(required_type=AsyncUserAuthenticationUseCase)
    with pytest.raises(AuthenticationFailedError):
        await usecase.execute(
            UserAuthenticationCommand(
                username="user",
                password="wrong",
            )
        )


@pytest.mark.asyncio
async def test_user_authentication_expect_succeed(
    context: ApplicationContext,
) -> None:
    repository = context.get(required_type=AsyncInMemoryUserRepository)
    await repository.save(
        User.create(
            username="user",
            password="password",
            email="test@email.com",
        )
    )
    usecase = context.get(required_type=AsyncUserAuthenticationUseCase)
    await usecase.execute(
        UserAuthenticationCommand(
            username="user",
            password="password",
        )
    )
