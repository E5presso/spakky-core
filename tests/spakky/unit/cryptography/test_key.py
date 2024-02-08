import pytest

from spakky.cryptography.base64_encoder import Base64Encoder
from spakky.cryptography.key import Key


def test_key_generate() -> None:
    b64: str = Base64Encoder.encode(utf8="Hello World!")
    key: Key = Key(base64=b64)
    assert key.b64 == "SGVsbG8gV29ybGQh"


def test_key_from_size() -> None:
    key: Key = Key(size=32)
    assert len(key.binary) == 32


def test_key_base64_url_safe() -> None:
    b64: str = Base64Encoder.encode(utf8="My Name is Michael! Nice to meet you!")
    key: Key = Key(base64=b64)
    assert (
        key.b64 == "TXkgTmFtZSBpcyBNaWNoYWVsISBOaWNlIHRvIG1lZXQgeW91IQ=="
        and key.b64_urlsafe == "TXkgTmFtZSBpcyBNaWNoYWVsISBOaWNlIHRvIG1lZXQgeW91IQ"
    )


def test_key_from_base64() -> None:
    key: Key = Key(
        base64="TXkgTmFtZSBpcyBNaWNoYWVsISBOaWNlIHRvIG1lZXQgeW91IQ==",
        url_safe=False,
    )
    assert key.binary.decode("utf-8") == "My Name is Michael! Nice to meet you!"


def test_key_from_base64_url_safe() -> None:
    key: Key = Key(
        base64="TXkgTmFtZSBpcyBNaWNoYWVsISBOaWNlIHRvIG1lZXQgeW91IQ",
        url_safe=True,
    )
    assert key.binary.decode("utf-8") == "My Name is Michael! Nice to meet you!"


def test_key_expect_value_error() -> None:
    with pytest.raises(ValueError):
        Key()  # type: ignore


def test_key_equals() -> None:
    k1: Key = Key(
        base64="TXkgTmFtZSBpcyBNaWNoYWVsISBOaWNlIHRvIG1lZXQgeW91IQ==",
        url_safe=False,
    )
    k2: Key = Key(
        base64="TXkgTmFtZSBpcyBNaWNoYWVsISBOaWNlIHRvIG1lZXQgeW91IQ==",
        url_safe=False,
    )
    assert k1 == k2


def test_key_not_equals() -> None:
    k1: Key = Key(size=32)
    k2: Key = Key(size=32)
    assert k1 != k2


def test_key_equals_expect_type_error() -> None:
    with pytest.raises(TypeError):
        assert Key(size=32) == 0


def test_key_length_not_equals() -> None:
    k1: Key = Key(size=32)
    k2: Key = Key(size=23)
    assert k1 != k2


def test_key_hex() -> None:
    key: Key = Key(binary=b"Hello World!")
    assert key.hex == "48656C6C6F20576F726C6421"
