from typing import ClassVar, overload

import bcrypt

from spakky.security.encoding import Base64Encoder
from spakky.security.key import Key
from spakky.security.password.interface import IPasswordEncoder


class BcryptPasswordEncoder(IPasswordEncoder):
    __salt: Key
    __hash: str
    __url_safe: bool
    ALGORITHM_TYPE: ClassVar[str] = "bcrypt"

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
    def __init__(self, *, password: str, url_safe: bool = False) -> None: ...

    def __init__(
        self,
        password_hash: str | None = None,
        password: str | None = None,
        url_safe: bool = False,
    ) -> None:
        self.__url_safe = url_safe
        if password_hash is not None:
            parts: list[str] = password_hash.split(":")
            parts.pop(0)
            self.__salt = Key(
                binary=Base64Encoder.get_bytes(parts[0], url_safe=self.__url_safe)
            )
            self.__hash = parts[1]
        else:
            if password is None:
                raise ValueError("parameter 'password' cannot be None")
            self.__salt = Key(binary=bcrypt.gensalt())
            self.__hash = Base64Encoder.from_bytes(
                bcrypt.hashpw(
                    password.encode("UTF-8"),
                    self.__salt.binary,
                ),
                url_safe=self.__url_safe,
            )

    def encode(self) -> str:
        return "{algorithm}:{salt}:{hash}".format(
            algorithm=self.ALGORITHM_TYPE,
            salt=self.__salt.b64_urlsafe if self.__url_safe else self.__salt.b64,
            hash=self.__hash,
        )

    def challenge(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("UTF-8"),
            Base64Encoder.get_bytes(self.__hash, url_safe=self.__url_safe),
        )
