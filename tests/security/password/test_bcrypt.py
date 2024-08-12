import pytest

from spakky.security.password.bcrypt import BcryptPasswordEncoder
from spakky.security.password.interface import IPasswordEncoder


def test_bcrypt_expect_value_error() -> None:
    with pytest.raises(ValueError):
        BcryptPasswordEncoder()  # type: ignore


def test_bcrypt_not_equal() -> None:
    p1: IPasswordEncoder = BcryptPasswordEncoder(password="pa55word!!")
    p2: IPasswordEncoder = BcryptPasswordEncoder(password="pa55word!!")
    assert p1 != p2


def test_bcrypt_from_hash() -> None:
    p1: IPasswordEncoder = BcryptPasswordEncoder(password="pa55word!!")
    p2: IPasswordEncoder = BcryptPasswordEncoder(password_hash=p1.encode())
    assert p1 == p2


def test_bcrypt_encode() -> None:
    p1: IPasswordEncoder = BcryptPasswordEncoder(password="pa55word!!")
    assert str(p1) == p1.encode()


def test_bcrypt_challenge() -> None:
    assert BcryptPasswordEncoder(password="Hello World").challenge("Hello World")


def test_bcrypt_hash() -> None:
    p1: IPasswordEncoder = BcryptPasswordEncoder(password="pa55word!!")
    p2: IPasswordEncoder = BcryptPasswordEncoder(password_hash=p1.encode())

    assert hash(p1) == hash(p2)
