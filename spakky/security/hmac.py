import hashlib
import hmac
from enum import Enum
from typing import Any, Callable, final

from spakky.security.encoding import Base64Encoder
from spakky.security.key import Key


@final
class HMACType(str, Enum):
    HS224 = "HS224"
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"


@final
class HMAC:
    @staticmethod
    def sign_text(
        key: Key,
        hmac_type: HMACType,
        content: str,
        url_safe: bool = False,
    ) -> str:
        key_bytes: bytes = key.binary
        hash_function: Callable[..., Any]
        match hmac_type:
            case HMACType.HS224:
                hash_function = hashlib.sha224
            case HMACType.HS256:
                hash_function = hashlib.sha256
            case HMACType.HS384:
                hash_function = hashlib.sha384
            case HMACType.HS512:
                hash_function = hashlib.sha512  # pragma: no cover
        return Base64Encoder.from_bytes(
            hmac.new(key_bytes, content.encode("UTF-8"), hash_function).digest(),
            url_safe,
        )

    @staticmethod
    def verify(
        key: Key,
        hmac_type: HMACType,
        content: str,
        signature: str,
        url_safe: bool = False,
    ) -> bool:
        key_bytes: bytes = key.binary
        hash_function: Callable[..., Any]
        match hmac_type:
            case HMACType.HS224:
                hash_function = hashlib.sha224
            case HMACType.HS256:
                hash_function = hashlib.sha256
            case HMACType.HS384:
                hash_function = hashlib.sha384
            case HMACType.HS512:
                hash_function = hashlib.sha512  # pragma: no cover
        return (
            Base64Encoder.from_bytes(
                hmac.new(key_bytes, content.encode("UTF-8"), hash_function).digest(),
                url_safe,
            )
            == signature
        )
