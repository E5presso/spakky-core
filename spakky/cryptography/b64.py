import base64
from typing import final


@final
class Base64Encoder:
    @classmethod
    def encode(cls, utf8: str, url_safe: bool = False) -> str:
        if url_safe:
            return base64.urlsafe_b64encode(utf8.encode("UTF-8")).decode("UTF-8").rstrip("=")
        return base64.b64encode(utf8.encode("UTF-8")).decode("UTF-8")

    @classmethod
    def decode(cls, b64: str, url_safe: bool = False) -> str:
        if url_safe:
            return base64.urlsafe_b64decode((b64 + ("=" * (4 - (len(b64) % 4)))).encode("UTF-8")).decode("UTF-8")
        return base64.b64decode(b64.encode("UTF-8")).decode("UTF-8")

    @classmethod
    def from_bytes(cls, bytes: bytes, url_safe: bool = False) -> str:
        if url_safe:
            return base64.urlsafe_b64encode(bytes).decode("UTF-8").rstrip("=")
        return base64.b64encode(bytes).decode("UTF-8")

    @classmethod
    def get_bytes(cls, b64: str, url_safe: bool = False) -> bytes:
        if url_safe:
            return base64.urlsafe_b64decode((b64 + ("=" * (4 - (len(b64) % 4)))).encode("UTF-8"))
        return base64.b64decode(b64.encode("UTF-8"))

    @classmethod
    def from_urlsafe(cls, b64_urlsafe: str) -> str:
        return cls.from_bytes(cls.get_bytes(b64_urlsafe, True), False)

    @classmethod
    def get_urlsafe(cls, b64: str) -> str:
        return cls.from_bytes(cls.get_bytes(b64, False), True)
