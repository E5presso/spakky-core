from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class ICryptor(Protocol):
    url_safe: bool

    @abstractmethod
    def encrypt(self, message: str) -> str:
        ...

    @abstractmethod
    def decrypt(self, cipher: str) -> str:
        ...
