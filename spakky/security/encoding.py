import base64
from typing import final


@final
class Base64Encoder:
    @staticmethod
    def encode(utf8: str, url_safe: bool = False) -> str:
        if url_safe:
            return (
                base64.urlsafe_b64encode(utf8.encode("UTF-8"))
                .decode("UTF-8")
                .rstrip("=")
            )
        return base64.b64encode(utf8.encode("UTF-8")).decode("UTF-8")

    @staticmethod
    def decode(b64: str, url_safe: bool = False) -> str:
        if url_safe:
            return base64.urlsafe_b64decode(
                (b64 + ("=" * (4 - (len(b64) % 4)))).encode("UTF-8")
            ).decode("UTF-8")
        return base64.b64decode(b64.encode("UTF-8")).decode("UTF-8")

    @staticmethod
    def from_bytes(binary: bytes, url_safe: bool = False) -> str:
        if url_safe:
            return base64.urlsafe_b64encode(binary).decode("UTF-8").rstrip("=")
        return base64.b64encode(binary).decode("UTF-8")

    @staticmethod
    def get_bytes(b64: str, url_safe: bool = False) -> bytes:
        if url_safe:
            return base64.urlsafe_b64decode(
                (b64 + ("=" * (4 - (len(b64) % 4)))).encode("UTF-8")
            )
        return base64.b64decode(b64.encode("UTF-8"))
