from typing import Protocol, runtime_checkable
from uuid import UUID

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import AbstractCommand, ICommandUseCase


@immutable
class SignupCommand(AbstractCommand):
    email: str
    password: str
    username: str


@runtime_checkable
class ISignupUseCase(ICommandUseCase[SignupCommand, UUID], Protocol): ...
