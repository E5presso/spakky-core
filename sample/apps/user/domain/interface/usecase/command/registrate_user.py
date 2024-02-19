from abc import ABC
from uuid import UUID

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase


@immutable
class RegistrateUserCommand(Command):
    username: str
    password: str
    email: str


class IAsyncRegistrateUserUseCase(IAsyncCommandUseCase[RegistrateUserCommand, UUID], ABC):
    ...
