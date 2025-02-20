from uuid import UUID

from spakky.pod.annotations.pod import Pod
from tests.application.apps.domain.port.usecase.signup import (
    ISignupUseCase,
    SignupCommand,
)


@Pod()
class UserController:
    __signup: ISignupUseCase

    def __init__(
        self,
        signup: ISignupUseCase,
    ) -> None:
        self.__signup = signup

    def signup(self, email: str, password: str, username: str) -> UUID:
        return self.__signup.execute(
            command=SignupCommand(
                email=email,
                password=password,
                username=username,
            )
        )
