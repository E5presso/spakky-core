from typing import ClassVar, final, overload

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import PKCS1_v1_5

from spakky.security.cryptography.interface import ICryptor, ISigner
from spakky.security.encoding import Base64Encoder
from spakky.security.error import (
    CannotImportAsymmetricKeyError,
    DecryptionFailedError,
    KeySizeError,
    PrivateKeyRequiredError,
)
from spakky.security.hash import Hash, HashType
from spakky.security.key import Key


@final
class AsymmetricKey:
    KEY_SIZES: ClassVar[list[int]] = [1024, 2048, 4096, 8192]
    __key: RsaKey
    __private_key: Key | None = None
    __public_key: Key

    @property
    def is_private(self) -> bool:
        return self.__private_key is not None

    @property
    def private_key(self) -> Key | None:
        return self.__private_key

    @property
    def public_key(self) -> Key:
        return self.__public_key

    @overload
    def __init__(self, *, key: str, passphrase: str | None = None) -> None: ...

    @overload
    def __init__(self, *, key: bytes, passphrase: str | None = None) -> None: ...

    @overload
    def __init__(self, *, size: int, passphrase: str | None = None) -> None: ...

    def __init__(
        self,
        key: str | bytes | None = None,
        size: int | None = None,
        passphrase: str | None = None,
    ) -> None:
        if key is None and size is None:  # pragma: no cover
            raise ValueError("'key' or 'size' must be specified")
        if key is not None:
            try:
                imported_key = RSA.import_key(key, passphrase)
                if (key_size := imported_key.size_in_bits()) not in self.KEY_SIZES:
                    raise KeySizeError(key_size * 8)
                self.__key = imported_key
            except (ValueError, IndexError, TypeError) as e:
                raise CannotImportAsymmetricKeyError from e
        if size is not None:
            if size not in self.KEY_SIZES:
                raise KeySizeError(size)
            self.__key = RSA.generate(size)
        if self.__key.has_private():
            self.__private_key = Key(
                binary=self.__key.export_key(passphrase=passphrase)
            )
        self.__public_key = Key(binary=self.__key.public_key().export_key())


@final
class Rsa(ICryptor, ISigner):
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
        if self.__key.private_key is None:
            raise PrivateKeyRequiredError
        try:
            cipher_bytes: bytes = Base64Encoder.get_bytes(cipher, self.url_safe)
            cryptor = PKCS1_OAEP.new(RSA.import_key(self.__key.private_key.binary))
            return cryptor.decrypt(cipher_bytes).decode()
        except Exception as e:
            raise DecryptionFailedError from e

    def sign(self, message: str, hash_type: HashType = HashType.SHA256) -> str:
        if self.__key.private_key is None:
            raise PrivateKeyRequiredError
        signer = PKCS1_v1_5.new(RSA.import_key(self.__key.private_key.binary))
        signature_bytes: bytes = signer.sign(Hash(message, hash_type))
        return Base64Encoder.from_bytes(signature_bytes, self.url_safe)

    def verify(
        self, message: str, signature: str, hash_type: HashType = HashType.SHA256
    ) -> bool:
        signature_bytes: bytes = Base64Encoder.get_bytes(signature, self.url_safe)
        signer = PKCS1_v1_5.new(RSA.import_key(self.__key.public_key.binary))
        return signer.verify(Hash(message, hash_type), signature_bytes)
