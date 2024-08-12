import random

import pytest

from spakky.security.cryptography.aes import Aes
from spakky.security.cryptography.interface import ICryptor
from spakky.security.error import DecryptionFailedError, KeySizeError
from spakky.security.key import Key


def test_aes() -> None:
    cryptor: ICryptor = Aes(key=Key(size=32))
    cipher: str = cryptor.encrypt("Hello World!")
    plain: str = cryptor.decrypt(cipher)
    assert plain == "Hello World!"
    with pytest.raises(DecryptionFailedError):
        tempered: list[str] = list(cipher)
        random.shuffle(tempered)
        tempered_cipher: str = "".join(tempered)
        plain = cryptor.decrypt(tempered_cipher)


def test_aes_expect_key_size_error() -> None:
    with pytest.raises(KeySizeError):
        Aes(key=Key(size=64))
