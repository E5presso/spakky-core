from sample.user.domain.interface.repository.user import IAsyncUserRepository
from sample.user.domain.interface.service.command.user_registration import (
    IAsyncUserRegistrationService,
    UserRegistrationCommand,
)
from sample.user.domain.model.user import User
from spakky.dependency.autowired import autowired
from spakky.domain.interfaces.event_publisher import IAsyncEventPublisher
from spakky.domain.interfaces.unit_of_work import AbstractAsyncUnitOfWork
from spakky.stereotypes.service import Service


@Service()
class AsyncUserRegistrationService(IAsyncUserRegistrationService):
    __transaction: AbstractAsyncUnitOfWork
    __user_repository: IAsyncUserRepository
    __event_publisher: IAsyncEventPublisher

    @autowired
    def __init__(
        self,
        transaction: AbstractAsyncUnitOfWork,
        user_repository: IAsyncUserRepository,
        event_publisher: IAsyncEventPublisher,
    ) -> None:
        self.__transaction = transaction
        self.__user_repository = user_repository
        self.__event_publisher = event_publisher

    async def execute(self, command: UserRegistrationCommand) -> None:
        async with self.__transaction:
            user: User = User.create(
                username=command.username,
                password=command.password,
                email=command.email,
            )
            await self.__user_repository.save(user)
            await self.__event_publisher.publish(user)
