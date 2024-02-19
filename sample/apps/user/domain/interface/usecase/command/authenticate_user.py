from abc import ABC

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase


@immutable
class AuthenticateUserCommand(Command):
    username: str
    password: str
    ip_address: str
    user_agent: str


class IAsyncAuthenticateUserUseCase(
    IAsyncCommandUseCase[AuthenticateUserCommand, str], ABC
):
    ...
