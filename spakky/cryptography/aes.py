from typing import final
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher._mode_cbc import CbcMode
from .cryptor import DecryptionError, ICryptor, KeySizeError
from .b64 import Base64Encoder
from .key import Key


@final
class Aes(ICryptor):
    __key: Key
    KEY_SIZE: int = 32

    def __init__(self, key: Key) -> None:
        if key.length != self.KEY_SIZE:
            raise KeySizeError(size=self.KEY_SIZE)
        self.__key = key

    def encrypt(self, message: str) -> str:
        plain_bytes: bytes = pad(message.encode("UTF-8"), AES.block_size)
        iv: Key = Key(size=16)
        cryptor: CbcMode = AES.new(key=self.__key.bytes, mode=AES.MODE_CBC, IV=iv.bytes)
        cipher_bytes: bytes = cryptor.encrypt(plain_bytes)
        return f"{iv.b64_urlsafe}:{Base64Encoder.from_bytes(cipher_bytes, True)}"

    def decrypt(self, cipher: str) -> str:
        try:
            [iv, cipher] = cipher.split(":")
            iv_bytes: bytes = Base64Encoder.get_bytes(iv, True)
            cipher_bytes: bytes = Base64Encoder.get_bytes(cipher, True)
            cryptor: CbcMode = AES.new(key=self.__key.bytes, mode=AES.MODE_CBC, IV=iv_bytes)
            plain_bytes: bytes = cryptor.decrypt(cipher_bytes)
            return unpad(plain_bytes, AES.block_size).decode("UTF-8")
        except:
            raise DecryptionError
