import secrets
from typing import Any, final, overload

from spakky.security.encoding import Base64Encoder


@final
class Key:
    __binary: bytes

    @overload
    def __init__(self, *, size: int) -> None: ...

    @overload
    def __init__(self, *, binary: bytes) -> None: ...

    @overload
    def __init__(self, *, base64: str, url_safe: bool = False) -> None: ...

    def __init__(
        self,
        size: int | None = None,
        binary: bytes | None = None,
        base64: str | None = None,
        url_safe: bool = False,
    ) -> None:
        if size is not None:
            self.__binary = secrets.token_bytes(size)
            return
        if binary is not None:
            self.__binary = binary
            return
        if base64 is not None:
            self.__binary = Base64Encoder.get_bytes(base64, url_safe=url_safe)
            return
        raise ValueError("Invalid call of constructor Key().")

    @property
    def binary(self) -> bytes:
        return self.__binary

    @property
    def length(self) -> int:
        return len(self.__binary)

    @property
    def b64(self) -> str:
        return Base64Encoder.from_bytes(self.__binary)

    @property
    def b64_urlsafe(self) -> str:
        return Base64Encoder.from_bytes(self.__binary, True)

    @property
    def hex(self) -> str:
        return self.__binary.hex().upper()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Key):
            raise TypeError
        return self.binary == other.binary

    def __ne__(self, other: Any) -> bool:
        return not self == other
