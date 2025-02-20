from hashlib import scrypt
from typing import ClassVar, overload

from spakky.security.encoding import Base64Encoder
from spakky.security.key import Key
from spakky.security.password.interface import IPasswordEncoder


class ScryptPasswordEncoder(IPasswordEncoder):
    __salt: Key
    __hash: str
    __n: int
    __r: int
    __p: int
    __maxmem: int
    __dklen: int
    __url_safe: bool
    ALGORITHM_TYPE: ClassVar[str] = "scrypt"
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
        n: int = 2**14,
        r: int = 8,
        p: int = 1,
        maxmem: int = 0,
        dklen: int = 32,
        url_safe: bool = False,
    ) -> None: ...

    def __init__(
        self,
        *,
        password_hash: str | None = None,
        password: str | None = None,
        salt: Key | None = None,
        n: int = 2**14,
        r: int = 8,
        p: int = 1,
        maxmem: int = 0,
        dklen: int = 32,
        url_safe: bool = False,
    ) -> None:
        self.__url_safe = url_safe
        if password_hash is not None:
            parts: list[str] = password_hash.split(":")
            parts.pop(0)
            self.__salt = Key(
                binary=Base64Encoder.get_bytes(parts[0], url_safe=self.__url_safe)
            )
            self.__n = int(parts[1])
            self.__r = int(parts[2])
            self.__p = int(parts[3])
            self.__maxmem = int(parts[4])
            self.__dklen = int(parts[5])
            self.__hash = parts[6]
        else:
            if password is None:
                raise ValueError("parameter 'password' cannot be None")
            if salt is None:
                salt = Key(size=self.SALT_SIZE)
            self.__salt = salt
            self.__n = n
            self.__r = r
            self.__p = p
            self.__maxmem = maxmem
            self.__dklen = dklen

            self.__hash = Base64Encoder.from_bytes(
                scrypt(
                    password.encode("UTF-8"),
                    salt=self.__salt.binary,
                    n=self.__n,
                    r=self.__r,
                    p=self.__p,
                    maxmem=self.__maxmem,
                    dklen=self.__dklen,
                ),
                url_safe=self.__url_safe,
            )

    def encode(self) -> str:
        return "{algorithm}:{salt}:{n}:{r}:{p}:{maxmem}:{dklen}:{hash}".format(
            algorithm=self.ALGORITHM_TYPE,
            salt=self.__salt.b64_urlsafe if self.__url_safe else self.__salt.b64,
            n=self.__n,
            r=self.__r,
            p=self.__p,
            maxmem=self.__maxmem,
            dklen=self.__dklen,
            hash=self.__hash,
        )

    def challenge(self, password: str) -> bool:
        return self.__hash == Base64Encoder.from_bytes(
            scrypt(
                password.encode("UTF-8"),
                salt=self.__salt.binary,
                n=self.__n,
                r=self.__r,
                p=self.__p,
                maxmem=self.__maxmem,
                dklen=self.__dklen,
            ),
            url_safe=self.__url_safe,
        )
