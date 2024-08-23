# pylint: disable=line-too-long

from datetime import timedelta

import pytest

from spakky.security.error import (
    InvalidJWTFormatError,
    JWTDecodingError,
    JWTProcessingError,
)
from spakky.security.hmac import HMACType
from spakky.security.jwt import JWT
from spakky.security.key import Key


def test_jwt_create() -> None:
    jwt: JWT = JWT()
    assert jwt.header["typ"] == "JWT"
    assert jwt.header["alg"] == HMACType.HS256
    assert jwt.payload != {}
    assert jwt.id is not None
    assert jwt.issued_at is not None
    assert jwt.updated_at is None
    assert jwt.last_authorized is None
    assert not jwt.is_expired
    assert not jwt.is_signed
    assert jwt.signature is None


def test_jwt_from_string() -> None:
    jwt: JWT = JWT(
        token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )
    assert jwt.header["typ"] == "JWT"
    assert jwt.header["alg"] == HMACType.HS256
    assert jwt.payload == {"sub": "1234567890", "name": "John Doe", "iat": 1516239022}
    assert jwt.id is None
    assert jwt.issued_at is not None
    assert jwt.updated_at is None
    assert jwt.last_authorized is None
    assert not jwt.is_expired
    assert jwt.signature == "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"


def test_jwt_from_string_expect_invalid_jwt_format_error() -> None:
    with pytest.raises(InvalidJWTFormatError):
        JWT(
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQSflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )


def test_jwt_from_string_expect_jwt_decoding_error() -> None:
    with pytest.raises(JWTDecodingError):
        JWT(
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyf.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )


def test_jwt_set_header() -> None:
    jwt: JWT = JWT()
    jwt.set_header(meta="META")

    assert jwt.header["meta"] == "META"


def test_jwt_set_header_signed() -> None:
    jwt: JWT = JWT()
    jwt.sign(Key(size=32))
    jwt.set_header(meta="META")

    assert jwt.header["meta"] == "META"


def test_jwt_set_payload() -> None:
    jwt: JWT = JWT()
    jwt.set_payload(age=29)

    assert jwt.payload["age"] == 29


def test_jwt_set_payload_signed() -> None:
    jwt: JWT = JWT()
    jwt.sign(Key(size=32))
    jwt.set_payload(age=29)

    assert jwt.payload["age"] == 29


def test_jwt_set_hash_type() -> None:
    jwt: JWT = JWT()
    assert jwt.hash_type == HMACType.HS256
    jwt.set_hash_type(HMACType.HS512)

    assert jwt.hash_type == HMACType.HS512


def test_jwt_set_hash_type_signed() -> None:
    jwt: JWT = JWT()
    jwt.sign(Key(size=32))
    assert jwt.hash_type == HMACType.HS256
    jwt.set_hash_type(HMACType.HS512)

    assert jwt.hash_type == HMACType.HS512


def test_jwt_set_expiration() -> None:
    jwt: JWT = JWT()
    jwt.set_expiration(timedelta(days=-1))
    assert jwt.is_expired


def test_jwt_set_expiration_signed() -> None:
    jwt: JWT = JWT()
    jwt.sign(Key(size=32))
    jwt.set_expiration(timedelta(days=-1))
    assert jwt.is_expired


def test_jwt_set_expiration_expect_jwt_processing_error() -> None:
    jwt: JWT = JWT(
        token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0.Gfx6VO9tcxwk6xqx9yYzSfebfeakZp5JYIgP_edcw_A"
    )
    with pytest.raises(
        JWTProcessingError, match="field named 'iat' does not exists in payload"
    ):
        jwt.set_expiration(timedelta(days=1))


def test_jwt_refresh() -> None:
    jwt: JWT = JWT()
    jwt.refresh(timedelta(days=-1))
    assert jwt.is_expired


def test_jwt_refresh_signed() -> None:
    jwt: JWT = JWT()
    jwt.sign(Key(size=32))
    jwt.refresh(timedelta(days=-1))
    assert jwt.is_expired


def test_jwt_sign() -> None:
    jwt: JWT = JWT()
    key: Key = Key(size=32)
    jwt.sign(key)
    assert jwt.signature is not None
    assert jwt.verify(key)


def test_jwt_verify() -> None:
    jwt: JWT = JWT()
    key: Key = Key(size=32)
    jwt.sign(key)
    assert jwt.verify(key)


def test_jwt_verify_expect_fail() -> None:
    jwt: JWT = JWT()
    key: Key = Key(size=32)
    jwt.sign(key)
    with pytest.raises(AssertionError):
        assert jwt.verify(Key(size=32))


def test_jwt_verify_expect_jwt_processing_error() -> None:
    jwt: JWT = JWT()
    with pytest.raises(JWTProcessingError, match="signature cannot be None"):
        jwt.verify(Key(size=32))


def test_jwt_export() -> None:
    jwt: JWT = JWT()
    jwt.sign(Key(size=32))
    assert jwt.export() != ""


def test_jwt_export_expect_jwt_processing_error() -> None:
    jwt: JWT = JWT()
    with pytest.raises(JWTProcessingError, match="Token must be signed"):
        jwt.export()
