from typing import final

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey

from spakky.cryptography.base64_encoder import Base64Encoder
from spakky.cryptography.cryptor.interface import ICryptor
from spakky.cryptography.error import (
    DecryptionFailedError,
    InvalidAsymmetricKeyFormatError,
    KeySizeError,
)
from spakky.cryptography.key import Key


@final
class AsymmetricKey:
    __key: RsaKey
    __private_key: Key
    __public_key: Key

    @property
    def private_key(self) -> Key:
        return self.__private_key

    @property
    def public_key(self) -> Key:
        return self.__public_key

    def __init__(
        self,
        key: bytes | None = None,
        passphrase: str | None = None,
        size: int | None = None,
    ) -> None:
        if key is None and size is None:  # pragma: no cover
            raise ValueError("'key' or 'size' must be specified")
        if key is not None:
            try:
                imported_key = RSA.import_key(key, passphrase)
                if (key_size := imported_key.size_in_bytes()) not in (128, 256):
                    raise KeySizeError(key_size * 8)
                self.__key = imported_key
            except (ValueError, IndexError, TypeError) as e:
                raise InvalidAsymmetricKeyFormatError from e
        if size is not None:
            if size not in (1024, 2048):
                raise KeySizeError(size)
            self.__key = RSA.generate(size)
        self.__private_key = Key(binary=self.__key.export_key())
        self.__public_key = Key(binary=self.__key.publickey().export_key())


@final
class Rsa(ICryptor):
    url_safe: bool
    __key: AsymmetricKey

    def __init__(self, key: AsymmetricKey, url_safe: bool = False) -> None:
        self.url_safe = url_safe
        self.__key = key

    def encrypt(self, message: str) -> str:
        cryptor = PKCS1_OAEP.new(RSA.import_key(self.__key.public_key.binary))
        cipher_bytes: bytes = cryptor.encrypt(message.encode())
        return Base64Encoder.from_bytes(cipher_bytes, self.url_safe)

    def decrypt(self, cipher: str) -> str:
        try:
            cipher_bytes: bytes = Base64Encoder.get_bytes(cipher, self.url_safe)
            cryptor = PKCS1_OAEP.new(RSA.import_key(self.__key.private_key.binary))
            return cryptor.decrypt(cipher_bytes).decode()
        except Exception as e:
            raise DecryptionFailedError from e
