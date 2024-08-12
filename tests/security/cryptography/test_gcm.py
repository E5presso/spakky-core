import random

import pytest

from spakky.security.cryptography.gcm import Gcm
from spakky.security.cryptography.interface import ICryptor
from spakky.security.error import DecryptionFailedError, KeySizeError
from spakky.security.key import Key


def test_gcm() -> None:
    cryptor: ICryptor = Gcm(key=Key(size=32))
    cipher: str = cryptor.encrypt("Hello World!")
    plain: str = cryptor.decrypt(cipher)
    assert plain == "Hello World!"
    with pytest.raises(DecryptionFailedError):
        tempered: list[str] = list(cipher)
        random.shuffle(tempered)
        tempered_cipher: str = "".join(tempered)
        plain = cryptor.decrypt(tempered_cipher)


def test_gcm_expect_key_size_error() -> None:
    with pytest.raises(KeySizeError):
        Gcm(key=Key(size=64))
