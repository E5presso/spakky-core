from abc import ABC
from uuid import UUID

from spakky.core.mutability import immutable
from spakky.domain.usecases.generic import IAsyncGenericUseCase, Request


@immutable
class UserRegistrationRequest(Request):
    username: str
    password: str
    email: str


class IAsyncUserRegistrationUseCase(
    IAsyncGenericUseCase[UserRegistrationRequest, UUID], ABC
):
    ...
