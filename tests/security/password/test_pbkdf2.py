import pytest

from spakky.security.hash import HashType
from spakky.security.key import Key
from spakky.security.password.interface import IPasswordEncoder
from spakky.security.password.pbkdf2 import Pbkdf2PasswordEncoder


def test_pbkdf2_expect_value_error() -> None:
    with pytest.raises(ValueError):
        Pbkdf2PasswordEncoder()  # type: ignore


def test_pbkdf2_not_equal() -> None:
    p1: IPasswordEncoder = Pbkdf2PasswordEncoder(password="pa55word!!")
    p2: IPasswordEncoder = Pbkdf2PasswordEncoder(password="pa55word!!")
    assert p1 != p2


def test_same_pbkdf2_equal() -> None:
    key: Key = Key(size=32)
    p1: IPasswordEncoder = Pbkdf2PasswordEncoder(password="pa55word!!", salt=key)
    p2: IPasswordEncoder = Pbkdf2PasswordEncoder(password="pa55word!!", salt=key)
    assert p1 == p2


def test_pbkdf2_from_hash() -> None:
    p1: IPasswordEncoder = Pbkdf2PasswordEncoder(password="pa55word!!")
    p2: IPasswordEncoder = Pbkdf2PasswordEncoder(password_hash=p1.encode())
    assert p1 == p2


def test_pbkdf2_string() -> None:
    key: Key = Key(size=32)
    p1: IPasswordEncoder = Pbkdf2PasswordEncoder(
        password="pa55word!!",
        salt=key,
        hash_type=HashType.SHA256,
        iteration=100000,
    )
    assert str(p1) == p1.encode()


def test_pbkdf2_challenge() -> None:
    assert Pbkdf2PasswordEncoder(password="Hello World").challenge("Hello World")


def test_pbkdf2_hash() -> None:
    key: Key = Key(size=32)
    p1: IPasswordEncoder = Pbkdf2PasswordEncoder(
        password="pa55word!!",
        salt=key,
        hash_type=HashType.SHA256,
        iteration=100000,
    )
    p2: IPasswordEncoder = Pbkdf2PasswordEncoder(
        password="pa55word!!",
        salt=key,
        hash_type=HashType.SHA256,
        iteration=100000,
    )
    assert hash(p1) == hash(p2)
