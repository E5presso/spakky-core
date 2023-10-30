from abc import ABC, abstractmethod
from typing import final


@final
class KeySizeError(BaseException):
    __size: int

    def __init__(self, size: int) -> None:
        self.__size = size

    def __str__(self) -> str:
        return f"Invalid key size. The only valid key size is {self.__size} bytes."


@final
class DecryptionError(BaseException):
    def __str__(self) -> str:
        return "Decryption failed. Check secret key or cipher message."


class ICryptor(ABC):
    @abstractmethod
    def encrypt(self, message: str) -> str:
        ...

    @abstractmethod
    def decrypt(self, cipher: str) -> str:
        ...
