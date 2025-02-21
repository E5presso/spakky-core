from spakky.application.application import SpakkyApplication
from tests.application.apps.adapter.api.users import UserController
from tests.application.apps.domain.port.repository.user import IUserRepository


def test_spakky_application(application: SpakkyApplication) -> None:
    controller = application.container.get(type_=UserController)
    user_id = controller.signup(
        email="email@test.com",
        password="password",
        username="username",
    )

    repository = application.container.get(type_=IUserRepository)
    user = repository.get(user_id)

    assert user.email == "email@test.com"
    assert user.password == "password"
    assert user.username == "username"
