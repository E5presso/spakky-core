from sample.apps.user.domain.interface.repository.user import IAsyncUserRepository
from sample.apps.user.domain.interface.service.token_service import IAsyncTokenService
from sample.apps.user.domain.interface.usecase.command.authenticate_user import (
    AuthenticateUserCommand,
    IAsyncAuthenticateUserUseCase,
)
from sample.apps.user.domain.model.user import AuthenticationFailedError, User
from sample.common.aspects.logging import AsyncLogging
from sample.common.aspects.transaction import AsyncTransactional
from spakky.dependency.autowired import autowired
from spakky.domain.interfaces.event_publisher import IAsyncEventPublisher
from spakky.stereotypes.usecase import UseCase


@UseCase()
class AsyncAuthenticateUserUseCase(IAsyncAuthenticateUserUseCase):
    __token_service: IAsyncTokenService
    __user_repository: IAsyncUserRepository
    __event_publisher: IAsyncEventPublisher

    @autowired
    def __init__(
        self,
        token_service: IAsyncTokenService,
        user_repository: IAsyncUserRepository,
        event_publisher: IAsyncEventPublisher,
    ) -> None:
        self.__token_service = token_service
        self.__user_repository = user_repository
        self.__event_publisher = event_publisher

    @AsyncLogging()
    @AsyncTransactional()
    async def execute(self, command: AuthenticateUserCommand) -> str:
        user: User | None = await self.__user_repository.get_by_username(command.username)
        if user is None:
            raise AuthenticationFailedError
        user.authenticate(
            command.password,
            command.ip_address,
            command.user_agent,
        )
        user = await self.__user_repository.save(user)
        await self.__event_publisher.publish(user)
        return await self.__token_service.generate_token(user)
