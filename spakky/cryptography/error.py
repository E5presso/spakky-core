from typing import final

from spakky.core.error import SpakkyCoreError


@final
class DecryptionFailedError(SpakkyCoreError):
    def __repr__(self) -> str:
        return "Decryption failed. Check secret key or cipher message."


@final
class KeySizeError(SpakkyCoreError):
    __size: int

    def __init__(self, size: int) -> None:
        self.__size = size

    def __repr__(self) -> str:
        return f"Invalid key size. The only valid key size is {self.__size} bytes."


@final
class InvalidJWTFormatError(SpakkyCoreError):
    def __repr__(self) -> str:
        return "parameter 'token' is not a valid data (which has 3 separated values.)"


@final
class JWTDecodingError(SpakkyCoreError):
    def __repr__(self) -> str:
        return "parameter 'token' is not a valid data (json decoding error.)"


@final
class JWTProcessingError(SpakkyCoreError):
    message: str

    def __init__(self, message: str) -> None:
        self.message = message

    def __repr__(self) -> str:
        return self.message
