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
    def __init__(self, *, password_hash: str) -> None:
        ...

    @overload
    def __init__(self, *, password: str) -> None:
        ...

    @overload
    def __init__(self, *, password: str, salt: Key) -> None:
        ...

    @overload
    def __init__(self, *, password: str, salt: Key, hash_type: HashType) -> None:
        ...

    @overload
    def __init__(
        self, *, password: str, salt: Key, hash_type: HashType, iteration: int
    ) -> None:
        ...

    def __init__(
        self,
        password_hash: str | None = None,
        password: str | None = None,
        salt: Key | None = None,
        hash_type: HashType = HashType.SHA256,
        iteration: int = 100000,
    ) -> None:
        if password_hash is not None:
            components: list[str] = password_hash.split(":")
            components.pop(0)
            self.__hash_type = HashType(components[0].upper())
            self.__iteration = int(components[1])
            self.__salt = Key(
                binary=Base64Encoder.get_bytes(components[2], url_safe=True)
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
                url_safe=True,
            )

    def __repr__(self) -> str:
        return f"pbkdf2:{self.__hash_type.lower()}:{self.__iteration}:{self.__salt.b64_urlsafe}:{self.__hash}"

    def __str__(self) -> str:
        return repr(self)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Password):
            raise TypeError
        return self.hash == other.hash

    def __ne__(self, other: Any) -> bool:
        return not self == other

    @classmethod
    def decompose(cls, password_hash: str) -> tuple[Key, HashType, int, str]:
        password: Password = Password(password_hash=password_hash)
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
