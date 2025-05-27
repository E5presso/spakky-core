from typing import ClassVar, final

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from spakky.security.cryptography.interface import ICryptor
from spakky.security.encoding import Base64Encoder
from spakky.security.error import DecryptionFailedError, KeySizeError
from spakky.security.key import Key


@final
class Gcm(ICryptor):
    KEY_SIZE: ClassVar[int] = 32
    url_safe: bool
    __key: Key

    def __init__(self, key: Key, url_safe: bool = False) -> None:
        if key.length != self.KEY_SIZE:
            raise KeySizeError
        self.url_safe = url_safe
        self.__key = key

    def encrypt(self, message: str) -> str:
        plain_bytes: bytes = pad(message.encode(), AES.block_size)
        aad: Key = Key(size=16)
        iv: Key = Key(size=12)
        cryptor = AES.new(  # type: ignore
            key=self.__key.binary,
            mode=AES.MODE_GCM,
            nonce=iv.binary,
        )
        cryptor.update(aad.binary)
        cipher_bytes, tag_bytes = cryptor.encrypt_and_digest(plain_bytes)
        return "{aad}:{tag}:{iv}:{cipher}".format(
            aad=aad.b64_urlsafe if self.url_safe else aad.b64,
            tag=Base64Encoder.from_bytes(tag_bytes, self.url_safe),
            iv=iv.b64_urlsafe if self.url_safe else iv.b64,
            cipher=Base64Encoder.from_bytes(cipher_bytes, self.url_safe),
        )

    def decrypt(self, cipher: str) -> str:
        try:
            [aad, tag, iv, cipher] = cipher.split(":")
            aad_bytes: bytes = Base64Encoder.get_bytes(aad, self.url_safe)
            tag_bytes: bytes = Base64Encoder.get_bytes(tag, self.url_safe)
            iv_bytes: bytes = Base64Encoder.get_bytes(iv, self.url_safe)
            cipher_bytes: bytes = Base64Encoder.get_bytes(cipher, self.url_safe)
            cryptor = AES.new(  # type: ignore
                key=self.__key.binary,
                mode=AES.MODE_GCM,
                nonce=iv_bytes,
            )
            cryptor.update(aad_bytes)
            plain_bytes: bytes = cryptor.decrypt_and_verify(cipher_bytes, tag_bytes)
            return unpad(plain_bytes, AES.block_size).decode()
        except Exception as e:
            raise DecryptionFailedError from e
