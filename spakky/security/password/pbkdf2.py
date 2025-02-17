import hashlib
from typing import ClassVar, overload

from spakky.security.encoding import Base64Encoder
from spakky.security.hash import HashType
from spakky.security.key import Key
from spakky.security.password.interface import IPasswordEncoder


class Pbkdf2PasswordEncoder(IPasswordEncoder):
    __salt: Key
    __iteration: int
    __hash_type: HashType
    __hash: str
    __url_safe: bool
    ALGORITHM_TYPE: ClassVar[str] = "pbkdf2"
    SALT_SIZE: ClassVar[int] = 32

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
        *,
        password_hash: str | None = None,
        password: str | None = None,
        salt: Key | None = None,
        hash_type: HashType = HashType.SHA256,
        iteration: int = 100000,
        url_safe: bool = False,
    ) -> None:
        self.__url_safe = url_safe
        if password_hash is not None:
            parts: list[str] = password_hash.split(":")
            parts.pop(0)
            self.__hash_type = HashType(parts[0].upper())
            self.__iteration = int(parts[1])
            self.__salt = Key(
                binary=Base64Encoder.get_bytes(parts[2], url_safe=self.__url_safe)
            )
            self.__hash = parts[3]
        else:
            if password is None:
                raise ValueError("parameter 'password' cannot be None")
            if salt is None:
                salt = Key(size=self.SALT_SIZE)
            self.__salt = salt
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
        return self.encode()

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, type(self)):
            return False
        return self.encode() == __value.encode()

    def __hash__(self) -> int:
        return hash(self.encode())

    def encode(self) -> str:
        return "{algorithm}:{hash_type}:{iteration}:{salt}:{hash}".format(
            algorithm=self.ALGORITHM_TYPE,
            hash_type=self.__hash_type.lower(),
            iteration=self.__iteration,
            salt=self.__salt.b64_urlsafe if self.__url_safe else self.__salt.b64,
            hash=self.__hash,
        )

    def challenge(self, password: str) -> bool:
        new_password: Pbkdf2PasswordEncoder = Pbkdf2PasswordEncoder(
            password=password,
            salt=self.__salt,
            hash_type=self.__hash_type,
            iteration=self.__iteration,
        )
        return self == new_password
