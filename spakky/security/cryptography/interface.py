from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.security.hash import HashType


@runtime_checkable
class ICryptor(Protocol):
    url_safe: bool

    @abstractmethod
    def encrypt(self, message: str) -> str: ...

    @abstractmethod
    def decrypt(self, cipher: str) -> str: ...


@runtime_checkable
class ISigner(Protocol):
    url_safe: bool

    @abstractmethod
    def sign(self, message: str, hash_type: HashType = HashType.SHA256) -> str: ...

    @abstractmethod
    def verify(
        self, message: str, signature: str, hash_type: HashType = HashType.SHA256
    ) -> bool: ...
