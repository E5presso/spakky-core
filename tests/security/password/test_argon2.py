import pytest

from spakky.security.key import Key
from spakky.security.password.argon2 import Argon2PasswordEncoder
from spakky.security.password.interface import IPasswordEncoder


def test_argon2_expect_value_error() -> None:
    with pytest.raises(ValueError):
        Argon2PasswordEncoder()  # type: ignore


def test_argon2_not_equal() -> None:
    p1: IPasswordEncoder = Argon2PasswordEncoder(password="pa55word!!")
    p2: IPasswordEncoder = Argon2PasswordEncoder(password="pa55word!!")
    assert p1 != p2


def test_argon2_with_same_salt_equal() -> None:
    salt: Key = Key(size=32)
    p1: IPasswordEncoder = Argon2PasswordEncoder(password="pa55word!!", salt=salt)
    p2: IPasswordEncoder = Argon2PasswordEncoder(password="pa55word!!", salt=salt)
    assert p1 == p2


def test_argon2_from_hash() -> None:
    p1: IPasswordEncoder = Argon2PasswordEncoder(password="pa55word!!")
    p2: IPasswordEncoder = Argon2PasswordEncoder(password_hash=p1.encode())
    assert p1 == p2


def test_argon2_encode() -> None:
    p1: IPasswordEncoder = Argon2PasswordEncoder(password="pa55word!!")
    assert str(p1) == p1.encode()


def test_argon2_challenge() -> None:
    assert Argon2PasswordEncoder(password="Hello World").challenge("Hello World")


def test_argon2_hash() -> None:
    p1: IPasswordEncoder = Argon2PasswordEncoder(password="pa55word!!")
    p2: IPasswordEncoder = Argon2PasswordEncoder(password_hash=p1.encode())

    assert hash(p1) == hash(p2)
