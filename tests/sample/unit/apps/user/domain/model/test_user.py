import pytest

from sample.apps.user.domain.model.user import (
    AuthenticationFailedError,
    EmailValidationFailedError,
    User,
)


def test_user_create_expect_email_validation_failed() -> None:
    with pytest.raises(EmailValidationFailedError):
        User.create(username="testuser", password="password", email="wrong")
    with pytest.raises(EmailValidationFailedError):
        User.create(username="testuser", password="password", email="wrong@email")
    with pytest.raises(EmailValidationFailedError):
        User.create(username="testuser", password="password", email="")
    with pytest.raises(EmailValidationFailedError):
        User.create(username="testuser", password="password", email="wrongemail.co.kr")


def test_user_create_expect_success() -> None:
    user: User = User.create(
        username="testuser",
        password="password",
        email="test@email.com",
    )

    assert user.username == "testuser"
    assert user.email == "test@email.com"
    assert user.password != "password"
    assert isinstance(user.events[0], User.Created)


def test_user_update_password_expect_password_authentication_failed() -> None:
    user: User = User.create(
        username="testuser",
        password="password",
        email="test@email.com",
    )
    with pytest.raises(AuthenticationFailedError):
        user.update_password("wrong", "new")


def test_user_update_password_expect_success() -> None:
    user: User = User.create(
        username="testuser",
        password="password",
        email="test@email.com",
    )
    user.update_password("password", "new")
    assert isinstance(user.events[1], User.PasswordUpdated)


def test_user_update_email_expect_validation_failed() -> None:
    user: User = User.create(
        username="testuser",
        password="password",
        email="test@email.com",
    )
    with pytest.raises(EmailValidationFailedError):
        user.update_email("wrong-email")

    assert user.email == "test@email.com"


def test_user_udpate_email_expect_success() -> None:
    user: User = User.create(
        username="testuser",
        password="password",
        email="test@email.com",
    )
    user.update_email("new@email.com")

    assert user.email == "new@email.com"
    assert isinstance(user.events[1], User.EmailUpdated)


def test_user_authenticate_expect_password_authentication_failed() -> None:
    user: User = User.create(
        username="testuser",
        password="password",
        email="test@email.com",
    )
    with pytest.raises(AuthenticationFailedError):
        user.authenticate("wrong")


def test_user_authenticate_expect_success() -> None:
    user: User = User.create(
        username="testuser",
        password="password",
        email="test@email.com",
    )
    user.authenticate("password")
    assert isinstance(user.events[1], User.Authenticated)
