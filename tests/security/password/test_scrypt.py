import pytest

from spakky.security.key import Key
from spakky.security.password.interface import IPasswordEncoder
from spakky.security.password.scrypt import ScryptPasswordEncoder


def test_scrypt_expect_value_error() -> None:
    with pytest.raises(ValueError):
        ScryptPasswordEncoder()  # type: ignore


def test_scrypt_not_equal() -> None:
    p1: IPasswordEncoder = ScryptPasswordEncoder(password="pa55word!!")
    p2: IPasswordEncoder = ScryptPasswordEncoder(password="pa55word!!")
    assert p1 != p2


def test_scrypt_with_same_salt_equal() -> None:
    salt: Key = Key(size=32)
    p1: IPasswordEncoder = ScryptPasswordEncoder(password="pa55word!!", salt=salt)
    p2: IPasswordEncoder = ScryptPasswordEncoder(password="pa55word!!", salt=salt)
    assert p1 == p2


def test_scrypt_from_hash() -> None:
    p1: IPasswordEncoder = ScryptPasswordEncoder(password="pa55word!!")
    p2: IPasswordEncoder = ScryptPasswordEncoder(password_hash=p1.encode())
    assert p1 == p2


def test_scrypt_encode() -> None:
    p1: IPasswordEncoder = ScryptPasswordEncoder(password="pa55word!!")
    assert str(p1) == p1.encode()


def test_scrypt_challenge() -> None:
    assert ScryptPasswordEncoder(password="Hello World").challenge("Hello World")


def test_scrypt_hash() -> None:
    p1: IPasswordEncoder = ScryptPasswordEncoder(password="pa55word!!")
    p2: IPasswordEncoder = ScryptPasswordEncoder(password_hash=p1.encode())

    assert hash(p1) == hash(p2)
