from typing import final
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher._mode_gcm import GcmMode
from .cryptor import DecryptionError, ICryptor, KeySizeError
from .b64 import Base64Encoder
from .key import Key


@final
class Gcm(ICryptor):
    __key: Key
    KEY_SIZE: int = 32

    def __init__(self, key: Key) -> None:
        if key.length != self.KEY_SIZE:
            raise KeySizeError(size=self.KEY_SIZE)
        self.__key = key

    def encrypt(self, message: str) -> str:
        plain_bytes: bytes = pad(message.encode("UTF-8"), AES.block_size)
        aad: Key = Key(size=16)
        iv: Key = Key(size=12)
        cryptor: GcmMode = AES.new(key=self.__key.bytes, mode=AES.MODE_GCM, nonce=iv.bytes)
        cryptor.update(aad.bytes)
        cipher_bytes, tag_bytes = cryptor.encrypt_and_digest(plain_bytes)
        return f"{aad.b64_urlsafe}:{Base64Encoder.from_bytes(tag_bytes, True)}:{iv.b64_urlsafe}:{Base64Encoder.from_bytes(cipher_bytes, True)}"

    def decrypt(self, cipher: str) -> str:
        try:
            [aad, tag, iv, cipher] = cipher.split(":")
            aad_bytes: bytes = Base64Encoder.get_bytes(aad, True)
            iv_bytes: bytes = Base64Encoder.get_bytes(iv, True)
            tag_bytes: bytes = Base64Encoder.get_bytes(tag, True)
            cipher_bytes: bytes = Base64Encoder.get_bytes(cipher, True)
            cryptor: GcmMode = AES.new(key=self.__key.bytes, mode=AES.MODE_GCM, nonce=iv_bytes)
            cryptor.update(aad_bytes)
            plain_bytes: bytes = cryptor.decrypt_and_verify(cipher_bytes, tag_bytes)
            return unpad(plain_bytes, AES.block_size).decode("UTF-8")
        except:
            raise DecryptionError
