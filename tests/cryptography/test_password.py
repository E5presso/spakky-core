import pytest

from spakky.cryptography.hash import HashType
from spakky.cryptography.key import Key
from spakky.cryptography.password import Password


def test_password_expect_value_error() -> None:
    with pytest.raises(ValueError):
        Password()  # type: ignore


def test_password_not_equal() -> None:
    p1: Password = Password(password="pa55word!!")
    p2: Password = Password(password="pa55word!!")
    assert p1 != p2


def test_same_password_equal() -> None:
    key: Key = Key(size=32)
    p1: Password = Password(password="pa55word!!", salt=key)
    p2: Password = Password(password="pa55word!!", salt=key)
    assert p1 == p2


def test_password_from_hash() -> None:
    p1: Password = Password(password="pa55word!!")
    p2: Password = Password(password_hash=p1.export)
    assert p1 == p2


def test_password_string() -> None:
    key: Key = Key(size=32)
    p1: Password = Password(
        password="pa55word!!",
        salt=key,
        hash_type=HashType.SHA256,
        iteration=100000,
    )
    assert p1.export == f"pbkdf2:sha256:100000:{key.b64}:{p1.hash}"


def test_password_decompose() -> None:
    key: Key = Key(base64="KBNyamQIZoDvYzgMqteB6kqlFldYRxHOrgWg_J4lxxs", url_safe=True)
    assert Password.decompose(
        "pbkdf2:sha256:100000:KBNyamQIZoDvYzgMqteB6kqlFldYRxHOrgWg_J4lxxs:sa1AUpPXKEAzgEsn35QaLbV_wNxovW6cgRwuCk2IyYs",
        url_safe=True,
    ) == (
        key,
        HashType.SHA256,
        100000,
        "sa1AUpPXKEAzgEsn35QaLbV_wNxovW6cgRwuCk2IyYs",
    )


def test_password_equals_expect_type_error() -> None:
    with pytest.raises(TypeError):
        assert Password(password="password") == 0


def test_password_challenge() -> None:
    assert Password(password="Hello World").challenge("Hello World")
