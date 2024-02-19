from abc import ABC
from uuid import UUID

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase


@immutable
class UserRegistrationCommand(Command):
    username: str
    password: str
    email: str


class IAsyncUserRegistrationUseCase(
    IAsyncCommandUseCase[UserRegistrationCommand, UUID], ABC
):
    ...
