import hashlib
from typing import Any, final, overload

from spakky.cryptography.base64_encoder import Base64Encoder
from spakky.cryptography.hash import HashType
from spakky.cryptography.key import Key


@final
class Password:
    __salt: Key
    __iteration: int
    __hash_type: HashType
    __hash: str
    __url_safe: bool

    @property
    def salt(self) -> Key:
        return self.__salt

    @property
    def iteration(self) -> int:
        return self.__iteration

    @property
    def hash_type(self) -> HashType:
        return self.__hash_type

    @property
    def hash(self) -> str:
        return self.__hash

    @property
    def export(self) -> str:
        return str(self)

    @overload
    def __init__(
        self,
        *,
        password_hash: str,
        url_safe: bool = False,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        password: str,
        salt: Key | None = None,
        hash_type: HashType = HashType.SHA256,
        iteration: int = 100000,
        url_safe: bool = False,
    ) -> None: ...

    def __init__(
        self,
        password_hash: str | None = None,
        password: str | None = None,
        salt: Key | None = None,
        hash_type: HashType = HashType.SHA256,
        iteration: int = 100000,
        url_safe: bool = False,
    ) -> None:
        self.__url_safe = url_safe
        if password_hash is not None:
            components: list[str] = password_hash.split(":")
            components.pop(0)
            self.__hash_type = HashType(components[0].upper())
            self.__iteration = int(components[1])
            self.__salt = Key(
                binary=Base64Encoder.get_bytes(components[2], url_safe=self.__url_safe)
            )
            self.__hash = components[3]
        else:
            if password is None:
                raise ValueError("parameter 'password' cannot be None")
            if salt is not None:
                self.__salt = salt
            else:
                self.__salt = Key(size=32)
            self.__hash_type = hash_type
            self.__iteration = iteration
            self.__hash: str = Base64Encoder.from_bytes(
                hashlib.pbkdf2_hmac(
                    self.__hash_type,
                    password.encode("UTF-8"),
                    self.__salt.binary,
                    self.__iteration,
                ),
                url_safe=self.__url_safe,
            )

    def __str__(self) -> str:
        return "pbkdf2:{hash_type}:{iteration}:{salt}:{hash}".format(
            hash_type=self.__hash_type.lower(),
            iteration=self.__iteration,
            salt=self.__salt.b64_urlsafe if self.__url_safe else self.__salt.b64,
            hash=self.__hash,
        )

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Password):
            raise TypeError
        return self.hash == other.hash

    def __ne__(self, other: Any) -> bool:
        return not self == other

    @classmethod
    def decompose(
        cls, password_hash: str, url_safe: bool = False
    ) -> tuple[Key, HashType, int, str]:
        password: Password = Password(password_hash=password_hash, url_safe=url_safe)
        return (
            password.salt,
            password.hash_type,
            password.iteration,
            password.hash,
        )

    def challenge(self, password: str) -> bool:
        new_password: Password = Password(
            password=password,
            salt=self.salt,
            hash_type=self.hash_type,
            iteration=self.iteration,
        )
        return self == new_password
