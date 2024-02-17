from uuid import UUID

from sample.apps.user.domain.interface.repository.user import IAsyncUserRepository
from sample.apps.user.domain.interface.usecase.command.user_registration import (
    IAsyncUserRegistrationUseCase,
    UserRegistrationRequest,
)
from sample.apps.user.domain.model.user import User
from sample.common.aspects.logging import async_logging
from sample.common.aspects.transaction import async_transactional
from spakky.dependency.autowired import autowired
from spakky.domain.interfaces.event_publisher import IAsyncEventPublisher
from spakky.stereotypes.usecase import UseCase


@UseCase()
class AsyncUserRegistrationUseCase(IAsyncUserRegistrationUseCase):
    __user_repository: IAsyncUserRepository
    __event_publisher: IAsyncEventPublisher

    @autowired
    def __init__(
        self,
        user_repository: IAsyncUserRepository,
        event_publisher: IAsyncEventPublisher,
    ) -> None:
        self.__user_repository = user_repository
        self.__event_publisher = event_publisher

    @async_logging
    @async_transactional
    async def execute(self, request: UserRegistrationRequest) -> UUID:
        user: User = User.create(
            username=request.username,
            password=request.password,
            email=request.email,
        )
        await self.__user_repository.save(user)
        await self.__event_publisher.publish(user)
        return user.uid
