from typing import final, overload
from .b64 import Base64Encoder
import secrets


@final
class Key:
    _key: bytes
    _url_safe: bool

    @overload
    def __init__(self, *, size: int) -> None:
        ...

    @overload
    def __init__(self, *, base64: str, url_safe: bool = False) -> None:
        ...

    def __init__(
        self,
        size: int | None = None,
        base64: str | None = None,
        url_safe: bool = False,
    ) -> None:
        if size is not None:
            self._key = secrets.token_bytes(size)
            self._url_safe = False
        elif base64 is not None:
            self._key = Base64Encoder.get_bytes(base64, url_safe=url_safe)
            self._url_safe = url_safe
        else:
            assert size is not None and base64 is not None
            assert size is None and base64 is None

    @property
    def bytes(self) -> bytes:
        return self._key

    @property
    def length(self) -> int:
        return len(self._key)

    @property
    def url_safe(self) -> bool:
        return self._url_safe

    @property
    def b64(self) -> str:
        return Base64Encoder.from_bytes(self._key)

    @property
    def b64_urlsafe(self) -> str:
        return Base64Encoder.from_bytes(self._key, True)

    @property
    def hex(self) -> str:
        return self._key.hex().upper()

    def __eq__(self, other) -> bool:
        if not isinstance(other, Key):
            raise TypeError
        return self._key == other._key

    def __ne__(self, other) -> bool:
        return not (self == other)
