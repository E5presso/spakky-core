from abc import ABC

from spakky.core.mutability import immutable
from spakky.domain.services.command import Command, IAsyncCommandService


@immutable
class UserRegistrationCommand(Command):
    username: str
    password: str
    email: str


class IAsyncUserRegistrationService(IAsyncCommandService[UserRegistrationCommand], ABC):
    ...
