from http import HTTPStatus
from uuid import UUID

from fastapi import Header, Response
from pydantic import BaseModel

from sample.apps.user.domain.error import (
    AuthenticationFailedError,
    EmailValidationFailedError,
    UserAlreadyExistsError,
)
from sample.apps.user.domain.interface.usecase.command.authenticate_user import (
    AuthenticateUserCommand,
    IAsyncAuthenticateUserUseCase,
)
from sample.apps.user.domain.interface.usecase.command.registrate_user import (
    IAsyncRegistrateUserUseCase,
    RegistrateUserCommand,
)
from sample.common.aspects.logging import AsyncLogging
from spakky.dependency.autowired import autowired
from spakky.plugin.fastapi.routing import post
from spakky.stereotypes.controller import Controller


class AuthenticateUser(BaseModel):
    username: str
    password: str


@Controller(prefix="/users/v1")
class UserApiController:
    user_registration_usecase: IAsyncRegistrateUserUseCase
    user_authentication_usecase: IAsyncAuthenticateUserUseCase

    @autowired
    def __init__(
        self,
        user_registration_usecase: IAsyncRegistrateUserUseCase,
        user_authentication_usecase: IAsyncAuthenticateUserUseCase,
    ) -> None:
        self.user_registration_usecase = user_registration_usecase
        self.user_authentication_usecase = user_authentication_usecase

    @AsyncLogging()
    @post(path="")
    async def registrate_user(self, command: RegistrateUserCommand) -> Response:
        try:
            uid: UUID = await self.user_registration_usecase.execute(command)
            return Response(content=str(uid), status_code=HTTPStatus.CREATED)
        except EmailValidationFailedError as e:
            return Response(content=e.message, status_code=HTTPStatus.BAD_REQUEST)
        except UserAlreadyExistsError as e:
            return Response(content=e.message, status_code=HTTPStatus.CONFLICT)

    @AsyncLogging()
    @post(path="/authenticate")
    async def authenticate_user(
        self,
        command: AuthenticateUser,
        x_forwarded_for: str | None = Header(default=None),
        ip_address: str | None = Header(default=None),
        user_agent: str | None = Header(default=None),
    ) -> Response:
        try:
            token: str = await self.user_authentication_usecase.execute(
                AuthenticateUserCommand(
                    username=command.username,
                    password=command.password,
                    ip_address=x_forwarded_for or ip_address or "0.0.0.0",
                    user_agent=user_agent or "Unknown",
                )
            )
            return Response(content=token, status_code=HTTPStatus.OK)
        except AuthenticationFailedError as e:
            return Response(content=e.message, status_code=HTTPStatus.UNAUTHORIZED)
