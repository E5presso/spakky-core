import hmac
import hashlib
from typing import Callable, final
from .b64 import Base64Encoder
from .hash import HashType
from .key import Key


@final
class HMAC:
    @classmethod
    def sign_text(
        cls,
        key: Key,
        hash_type: HashType,
        content: str,
        url_safe: bool = False,
    ) -> str:
        key_bytes: bytes = key.bytes
        hash_function: Callable
        match hash_type:
            case HashType.MD5:
                hash_function = hashlib.md5
            case HashType.SHA1:
                hash_function = hashlib.sha1
            case HashType.SHA224:
                hash_function = hashlib.sha224
            case HashType.SHA256 | HashType.HS256:
                hash_function = hashlib.sha256
            case HashType.SHA384 | HashType.HS384:
                hash_function = hashlib.sha384
            case HashType.SHA512 | HashType.HS512:
                hash_function = hashlib.sha512
        return Base64Encoder.from_bytes(
            hmac.new(key_bytes, content.encode("UTF-8"), hash_function).digest(),
            url_safe,
        )

    @classmethod
    def verify(
        cls,
        key: Key,
        hash_type: HashType,
        content: str,
        signature: str,
        url_safe: bool = False,
    ) -> bool:
        key_bytes: bytes = key.bytes
        hash_function: Callable
        match hash_type:
            case HashType.MD5:
                hash_function = hashlib.md5
            case HashType.SHA1:
                hash_function = hashlib.sha1
            case HashType.SHA224:
                hash_function = hashlib.sha224
            case HashType.SHA256 | HashType.HS256:
                hash_function = hashlib.sha256
            case HashType.SHA384 | HashType.HS384:
                hash_function = hashlib.sha384
            case HashType.SHA512 | HashType.HS512:
                hash_function = hashlib.sha512
        return (
            Base64Encoder.from_bytes(
                hmac.new(key_bytes, content.encode("UTF-8"), hash_function).digest(),
                url_safe,
            )
            == signature
        )
