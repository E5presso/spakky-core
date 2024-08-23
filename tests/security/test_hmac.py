from spakky.security.hmac import HMAC, HMACType
from spakky.security.key import Key

MESSAGE: str = "Hello World! I'm Program!"


def test_hmac_hs224() -> None:
    key: Key = Key(size=32)
    signature: str = HMAC.sign_text(
        key=key,
        hmac_type=HMACType.HS224,
        content=MESSAGE,
    )
    assert HMAC.verify(
        key=key,
        hmac_type=HMACType.HS224,
        content=MESSAGE,
        signature=signature,
    )


def test_hmac_hs256() -> None:
    key: Key = Key(size=32)
    signature: str = HMAC.sign_text(
        key=key,
        hmac_type=HMACType.HS256,
        content=MESSAGE,
    )
    assert HMAC.verify(
        key=key,
        hmac_type=HMACType.HS256,
        content=MESSAGE,
        signature=signature,
    )


def test_hmac_hs384() -> None:
    key: Key = Key(size=32)
    signature: str = HMAC.sign_text(
        key=key,
        hmac_type=HMACType.HS384,
        content=MESSAGE,
    )
    assert HMAC.verify(
        key=key,
        hmac_type=HMACType.HS384,
        content=MESSAGE,
        signature=signature,
    )


def test_hmac_hs512() -> None:
    key: Key = Key(size=32)
    signature: str = HMAC.sign_text(
        key=key,
        hmac_type=HMACType.HS512,
        content=MESSAGE,
    )
    assert HMAC.verify(
        key=key,
        hmac_type=HMACType.HS512,
        content=MESSAGE,
        signature=signature,
    )
