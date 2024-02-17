from uuid import UUID

from sample.apps.user.domain.interface.usecase.command.user_authentication import (
    IAsyncUserAuthenticationUseCase,
    UserAuthenticationCommand,
)
from sample.apps.user.domain.interface.usecase.command.user_registration import (
    IAsyncUserRegistrationUseCase,
    UserRegistrationRequest,
)
from spakky.dependency.autowired import autowired
from spakky.plugin.fastapi.routing import post
from spakky.stereotypes.controller import Controller


@Controller(prefix="/users/v1")
class UserApiController:
    user_registration_usecase: IAsyncUserRegistrationUseCase

    @autowired
    def __init__(
        self,
        user_registration_usecase: IAsyncUserRegistrationUseCase,
        user_authentication_usecase: IAsyncUserAuthenticationUseCase,
    ) -> None:
        self.user_registration_usecase = user_registration_usecase
        self.user_authentication_usecase = user_authentication_usecase

    @post(path="")
    async def registrate_user(self, request: UserRegistrationRequest) -> UUID:
        return await self.user_registration_usecase.execute(request)

    @post(path="/authenticate")
    async def authenticate_user(self, command: UserAuthenticationCommand) -> None:
        return await self.user_authentication_usecase.execute(command)
