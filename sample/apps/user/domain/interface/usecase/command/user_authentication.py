from abc import ABC

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase


@immutable
class UserAuthenticationCommand(Command):
    username: str
    password: str


class IAsyncUserAuthenticationUseCase(
    IAsyncCommandUseCase[UserAuthenticationCommand], ABC
):
    ...
