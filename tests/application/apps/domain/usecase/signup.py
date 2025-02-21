from uuid import UUID

from spakky.aspects.logging import Logging
from spakky.aspects.transactional import Transactional
from spakky.pod.annotations.pod import Pod
from tests.application.apps.domain.model.user import User
from tests.application.apps.domain.port.repository.user import IUserRepository
from tests.application.apps.domain.port.usecase.signup import (
    ISignupUseCase,
    SignupCommand,
)


@Pod()
class SignupUseCase(ISignupUseCase):
    _repository: IUserRepository

    def __init__(self, repository: IUserRepository) -> None:
        self._repository = repository

    @Logging()
    @Transactional()
    def execute(self, command: SignupCommand) -> UUID:
        user = User.create(
            email=command.email,
            password=command.password,
            username=command.username,
        )
        self._repository.save(user)
        return user.uid
