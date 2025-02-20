from typing import ClassVar, overload

from argon2 import PasswordHasher

from spakky.security.encoding import Base64Encoder
from spakky.security.key import Key
from spakky.security.password.interface import IPasswordEncoder


class Argon2PasswordEncoder(IPasswordEncoder):
    __salt: Key
    __time_cost: int
    __memory_cost: int
    __parallelism: int
    __hash_len: int
    __salt_len: int
    __hash: str
    ALGORITHM_TYPE: ClassVar[str] = "argon2"
    SALT_SIZE: ClassVar[int] = 32

    def __str__(self) -> str:
        return self.encode()

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, type(self)):
            return False
        return self.encode() == __value.encode()

    def __hash__(self) -> int:
        return hash(self.encode())

    @overload
    def __init__(self, *, password_hash: str, url_safe: bool = False) -> None: ...

    @overload
    def __init__(
        self,
        *,
        password: str,
        salt: Key | None = None,
        time_cost: int = 3,
        memory_cost: int = 65536,
        parallelism: int = 4,
        hash_len: int = 32,
        url_safe: bool = False,
    ) -> None: ...

    def __init__(
        self,
        *,
        password_hash: str | None = None,
        password: str | None = None,
        salt: Key | None = None,
        time_cost: int = 3,
        memory_cost: int = 65536,
        parallelism: int = 4,
        hash_len: int = 32,
        url_safe: bool = False,
    ) -> None:
        self.__url_safe = url_safe
        if password_hash is not None:
            parts: list[str] = password_hash.split(":")
            parts.pop(0)
            self.__salt = Key(
                binary=Base64Encoder.get_bytes(parts[0], url_safe=self.__url_safe)
            )
            self.__time_cost = int(parts[1])
            self.__memory_cost = int(parts[2])
            self.__parallelism = int(parts[3])
            self.__hash_len = int(parts[4])
            self.__salt_len = self.__salt.length
            self.__hash = parts[5]
        else:
            if password is None:
                raise ValueError("parameter 'password' cannot be None")
            if salt is None:
                salt = Key(size=self.SALT_SIZE)
            self.__salt = salt
            self.__time_cost = time_cost
            self.__memory_cost = memory_cost
            self.__parallelism = parallelism
            self.__hash_len = hash_len
            self.__salt_len = salt.length
            self.__hash = Base64Encoder.from_bytes(
                binary=PasswordHasher(
                    time_cost=self.__time_cost,
                    memory_cost=self.__memory_cost,
                    parallelism=self.__parallelism,
                    hash_len=self.__hash_len,
                    salt_len=self.__salt_len,
                )
                .hash(password.encode("UTF-8"), salt=self.__salt.binary)
                .encode("UTF-8"),
                url_safe=self.__url_safe,
            )

    def encode(self) -> str:
        return "{algorithm}:{salt}:{time_cost}:{memory_cost}:{parallelism}:{hash_len}:{hash}".format(
            algorithm=self.ALGORITHM_TYPE,
            salt=self.__salt.b64_urlsafe if self.__url_safe else self.__salt.b64,
            time_cost=self.__time_cost,
            memory_cost=self.__memory_cost,
            parallelism=self.__parallelism,
            hash_len=self.__hash_len,
            hash=self.__hash,
        )

    def challenge(self, password: str) -> bool:
        return PasswordHasher(
            time_cost=self.__time_cost,
            memory_cost=self.__memory_cost,
            parallelism=self.__parallelism,
            hash_len=self.__hash_len,
            salt_len=self.__salt_len,
        ).verify(
            Base64Encoder.get_bytes(self.__hash, self.__url_safe),
            password.encode("UTF-8"),
        )
