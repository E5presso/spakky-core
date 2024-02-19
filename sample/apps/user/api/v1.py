from http import HTTPStatus
from uuid import UUID

from fastapi import Response

from sample.apps.user.domain.error import (
    AuthenticationFailedError,
    EmailValidationFailedError,
    UserAlreadyExistsError,
)
from sample.apps.user.domain.interface.usecase.command.user_authentication import (
    IAsyncUserAuthenticationUseCase,
    UserAuthenticationCommand,
)
from sample.apps.user.domain.interface.usecase.command.user_registration import (
    IAsyncUserRegistrationUseCase,
    UserRegistrationCommand,
)
from sample.common.aspects.logging import async_logging
from spakky.dependency.autowired import autowired
from spakky.plugin.fastapi.routing import post
from spakky.stereotypes.controller import Controller


@Controller(prefix="/users/v1")
class UserApiController:
    user_registration_usecase: IAsyncUserRegistrationUseCase
    user_authentication_usecase: IAsyncUserAuthenticationUseCase

    @autowired
    def __init__(
        self,
        user_registration_usecase: IAsyncUserRegistrationUseCase,
        user_authentication_usecase: IAsyncUserAuthenticationUseCase,
    ) -> None:
        self.user_registration_usecase = user_registration_usecase
        self.user_authentication_usecase = user_authentication_usecase

    @async_logging
    @post(path="")
    async def registrate_user(self, command: UserRegistrationCommand) -> Response:
        try:
            uid: UUID = await self.user_registration_usecase.execute(command)
            return Response(content=str(uid), status_code=HTTPStatus.CREATED)
        except EmailValidationFailedError as e:
            return Response(content=e.message, status_code=HTTPStatus.BAD_REQUEST)
        except UserAlreadyExistsError as e:
            return Response(content=e.message, status_code=HTTPStatus.CONFLICT)

    @async_logging
    @post(path="/authenticate")
    async def authenticate_user(self, command: UserAuthenticationCommand) -> Response:
        try:
            await self.user_authentication_usecase.execute(command)
            return Response(status_code=HTTPStatus.OK)
        except AuthenticationFailedError as e:
            return Response(content=e.message, status_code=HTTPStatus.UNAUTHORIZED)
