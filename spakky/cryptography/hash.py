from io import BufferedReader
from enum import Enum
from typing import final
from hashlib import md5, sha1, sha224, sha256, sha384, sha512

from spakky.cryptography.base64_encoder import Base64Encoder


@final
class HashType(str, Enum):
    MD5 = "MD5"
    SHA1 = "SHA1"
    SHA224 = "SHA224"
    SHA256 = "SHA256"
    SHA384 = "SHA384"
    SHA512 = "SHA512"


@final
class Hash:
    __hash_type: HashType

    def __init__(
        self, data: str | BufferedReader, hash_type: HashType = HashType.SHA256
    ) -> None:
        self.__hash_type = hash_type
        match self.__hash_type:
            case HashType.MD5:
                self.__hash = md5()
            case HashType.SHA1:
                self.__hash = sha1()
            case HashType.SHA224:
                self.__hash = sha224()
            case HashType.SHA256:
                self.__hash = sha256()
            case HashType.SHA384:
                self.__hash = sha384()
            case HashType.SHA512:  # pragma: no cover
                self.__hash = sha512()
        if isinstance(data, str):
            self.__hash.update(data.encode("UTF-8"))
        if isinstance(data, BufferedReader):
            while True:
                buffer: bytes = data.read(65536)
                if not any(buffer):
                    break
                self.__hash.update(buffer)

    @property
    def hex(self) -> str:
        return self.__hash.hexdigest().upper()

    @property
    def b64(self) -> str:
        return Base64Encoder.from_bytes(self.__hash.digest())

    @property
    def b64_urlsafe(self) -> str:
        return Base64Encoder.from_bytes(self.__hash.digest(), url_safe=True)

    @property
    def bytes(self) -> bytes:
        return self.__hash.digest()
