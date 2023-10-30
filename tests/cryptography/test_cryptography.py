import random
import pytest
from spakky.cryptography.aes import Aes
from spakky.cryptography.gcm import Gcm
from spakky.cryptography.cryptor import DecryptionError, ICryptor
from spakky.cryptography.key import Key
from spakky.cryptography.hash import Hash, HashType
from spakky.cryptography.b64 import Base64Encoder
from spakky.cryptography.hmac import HMAC, HashType
from spakky.cryptography.password import Password


MESSAGE: str = "Hello World! I'm Program!"


def test_cryptor() -> None:
    key: Key = Key(size=32)
    message: str = "Hello World!"
    encryptor: Aes = Aes(key)
    decryptor: Aes = Aes(key)
    cipher: str = encryptor.encrypt(message)
    plain: str = decryptor.decrypt(cipher)
    assert message == plain


def test_base64_from_utf8() -> None:
    b64: str = Base64Encoder.encode(utf8=MESSAGE)
    assert b64 == "SGVsbG8gV29ybGQhIEknbSBQcm9ncmFtIQ=="


def test_base64_from_utf8_url_safe() -> None:
    b64: str = Base64Encoder.encode(utf8=MESSAGE, url_safe=True)
    assert b64 == "SGVsbG8gV29ybGQhIEknbSBQcm9ncmFtIQ"


def test_utf8_from_base64() -> None:
    utf8: str = Base64Encoder.decode(b64="SGVsbG8gV29ybGQhIEknbSBQcm9ncmFtIQ==")
    assert utf8 == MESSAGE


def test_utf8_from_base64_url_safe() -> None:
    utf8: str = Base64Encoder.decode(
        b64="SGVsbG8gV29ybGQhIEknbSBQcm9ncmFtIQ",
        url_safe=True,
    )
    assert utf8 == MESSAGE


def test_base64_from_bytes() -> None:
    b64: str = Base64Encoder.from_bytes(
        bytes=bytes(
            [
                0x00,
                0x01,
                0x02,
                0x03,
                0x04,
                0x05,
                0x06,
                0x07,
                0x08,
                0x09,
                0x0A,
                0x0B,
                0x0C,
                0x0D,
                0x0E,
                0x0F,
            ]
        )
    )
    assert b64 == "AAECAwQFBgcICQoLDA0ODw=="


def test_bytes_from_base64() -> None:
    b64: str = "AAECAwQFBgcICQoLDA0ODw=="
    assert Base64Encoder.get_bytes(b64=b64) == bytes(
        [
            0x00,
            0x01,
            0x02,
            0x03,
            0x04,
            0x05,
            0x06,
            0x07,
            0x08,
            0x09,
            0x0A,
            0x0B,
            0x0C,
            0x0D,
            0x0E,
            0x0F,
        ]
    )


def test_base64_from_bytes_url_safe() -> None:
    b64: str = Base64Encoder.from_bytes(
        bytes=bytes(
            [
                0x00,
                0x01,
                0x02,
                0x03,
                0x04,
                0x05,
                0x06,
                0x07,
                0x08,
                0x09,
                0x0A,
                0x0B,
                0x0C,
                0x0D,
                0x0E,
                0x0F,
            ]
        ),
        url_safe=True,
    )
    assert b64 == "AAECAwQFBgcICQoLDA0ODw"


def test_bytes_from_base64_url_safe() -> None:
    b64: str = "AAECAwQFBgcICQoLDA0ODw"
    assert Base64Encoder.get_bytes(b64=b64, url_safe=True) == bytes(
        [
            0x00,
            0x01,
            0x02,
            0x03,
            0x04,
            0x05,
            0x06,
            0x07,
            0x08,
            0x09,
            0x0A,
            0x0B,
            0x0C,
            0x0D,
            0x0E,
            0x0F,
        ]
    )


def test_md5() -> None:
    hash: Hash = Hash("Hello World!", hash_type=HashType.MD5)
    assert hash.hex == "ED076287532E86365E841E92BFC50D8C"


def test_sha1() -> None:
    hash: Hash = Hash("Hello World!", hash_type=HashType.SHA1)
    assert hash.hex == "2EF7BDE608CE5404E97D5F042F95F89F1C232871"


def test_sha224() -> None:
    hash: Hash = Hash("Hello World!", hash_type=HashType.SHA224)
    assert hash.hex == "4575BB4EC129DF6380CEDDE6D71217FE0536F8FFC4E18BCA530A7A1B"


def test_sha256() -> None:
    hash: Hash = Hash("Hello World!", hash_type=HashType.SHA256)
    assert hash.hex == "7F83B1657FF1FC53B92DC18148A1D65DFC2D4B1FA3D677284ADDD200126D9069"


def test_sha384() -> None:
    hash: Hash = Hash("Hello World!", hash_type=HashType.SHA384)
    assert (
        hash.hex == "BFD76C0EBBD006FEE583410547C1887B0292BE76D582D96C242D2A792723E3FD6FD061F9D5CFD13B8F961358E6ADBA4A"
    )


def test_sha512() -> None:
    hash: Hash = Hash("Hello World!", hash_type=HashType.SHA512)
    assert (
        hash.hex
        == "861844D6704E8573FEC34D967E20BCFEF3D424CF48BE04E6DC08F2BD58C729743371015EAD891CC3CF1C9D34B49264B510751B1FF9E537937BC46B5D6FF4ECC8"
    )


def test_hmac_md5() -> None:
    key: Key = Key(size=32)
    signature: str = HMAC.sign_text(
        key=key,
        hash_type=HashType.MD5,
        content=MESSAGE,
    )
    assert HMAC.verify(
        key=key,
        hash_type=HashType.MD5,
        content=MESSAGE,
        signature=signature,
    )


def test_hmac_sha1() -> None:
    key: Key = Key(size=32)
    signature: str = HMAC.sign_text(
        key=key,
        hash_type=HashType.SHA1,
        content=MESSAGE,
    )
    assert HMAC.verify(
        key=key,
        hash_type=HashType.SHA1,
        content=MESSAGE,
        signature=signature,
    )


def test_hmac_hs256() -> None:
    key: Key = Key(size=32)
    signature: str = HMAC.sign_text(
        key=key,
        hash_type=HashType.HS256,
        content=MESSAGE,
    )
    assert HMAC.verify(
        key=key,
        hash_type=HashType.HS256,
        content=MESSAGE,
        signature=signature,
    )


def test_hmac_hs384() -> None:
    key: Key = Key(size=32)
    signature: str = HMAC.sign_text(
        key=key,
        hash_type=HashType.HS384,
        content=MESSAGE,
    )
    assert HMAC.verify(
        key=key,
        hash_type=HashType.HS384,
        content=MESSAGE,
        signature=signature,
    )


def test_hmac_hs512() -> None:
    key: Key = Key(size=32)
    signature: str = HMAC.sign_text(
        key=key,
        hash_type=HashType.HS512,
        content=MESSAGE,
    )
    assert HMAC.verify(
        key=key,
        hash_type=HashType.HS512,
        content=MESSAGE,
        signature=signature,
    )


def test_key_generate() -> None:
    b64: str = Base64Encoder.encode(utf8="Hello World!")
    key: Key = Key(base64=b64)
    assert key.b64 == "SGVsbG8gV29ybGQh"


def test_key_from_size() -> None:
    key: Key = Key(size=32)
    assert len(key.bytes) == 32


def test_key_base64_url_safe() -> None:
    b64: str = Base64Encoder.encode(utf8="My Name is Michael! Nice to meet you!")
    key: Key = Key(base64=b64)
    assert (
        key.b64 == "TXkgTmFtZSBpcyBNaWNoYWVsISBOaWNlIHRvIG1lZXQgeW91IQ=="
        and key.b64_urlsafe == "TXkgTmFtZSBpcyBNaWNoYWVsISBOaWNlIHRvIG1lZXQgeW91IQ"
    )


def test_key_from_base64() -> None:
    key: Key = Key(
        base64="TXkgTmFtZSBpcyBNaWNoYWVsISBOaWNlIHRvIG1lZXQgeW91IQ==",
        url_safe=False,
    )
    assert key.bytes.decode("utf-8") == "My Name is Michael! Nice to meet you!"


def test_key_from_base64_url_safe() -> None:
    key: Key = Key(
        base64="TXkgTmFtZSBpcyBNaWNoYWVsISBOaWNlIHRvIG1lZXQgeW91IQ",
        url_safe=True,
    )
    assert key.bytes.decode("utf-8") == "My Name is Michael! Nice to meet you!"


def test_key_equals() -> None:
    k1: Key = Key(
        base64="TXkgTmFtZSBpcyBNaWNoYWVsISBOaWNlIHRvIG1lZXQgeW91IQ==",
        url_safe=False,
    )
    k2: Key = Key(
        base64="TXkgTmFtZSBpcyBNaWNoYWVsISBOaWNlIHRvIG1lZXQgeW91IQ==",
        url_safe=False,
    )
    assert k1 == k2


def test_key_not_equals() -> None:
    k1: Key = Key(size=32)
    k2: Key = Key(size=32)
    assert k1 != k2


def test_key_length_not_equals() -> None:
    k1: Key = Key(size=32)
    k2: Key = Key(size=23)
    assert k1 != k2


def test_password_not_equal() -> None:
    p1: Password = Password(password="pa55word!!")
    p2: Password = Password(password="pa55word!!")
    assert p1 != p2


def test_same_password_equal() -> None:
    key: Key = Key(size=32)
    p1: Password = Password(password="pa55word!!", salt=key)
    p2: Password = Password(password="pa55word!!", salt=key)
    assert p1 == p2


def test_password_from_hash() -> None:
    p1: Password = Password(password="pa55word!!")
    p2: Password = Password(hash=p1.export)
    assert p1 == p2


def test_password_string() -> None:
    key: Key = Key(size=32)
    p1: Password = Password(
        password="pa55word!!",
        salt=key,
        hash_type=HashType.SHA256,
        iteration=100000,
    )
    assert p1.export == f"pbkdf2:sha256:100000:{key.b64_urlsafe}:{p1.hash}"


def test_password_decompose() -> None:
    key: Key = Key(base64="KBNyamQIZoDvYzgMqteB6kqlFldYRxHOrgWg_J4lxxs", url_safe=True)
    assert Password.decompose(
        "pbkdf2:sha256:100000:KBNyamQIZoDvYzgMqteB6kqlFldYRxHOrgWg_J4lxxs:sa1AUpPXKEAzgEsn35QaLbV_wNxovW6cgRwuCk2IyYs"
    ) == (
        key,
        HashType.SHA256,
        100000,
        "sa1AUpPXKEAzgEsn35QaLbV_wNxovW6cgRwuCk2IyYs",
    )


def test_aes() -> None:
    cryptor: ICryptor = Aes(key=Key(size=32))
    cipher: str = cryptor.encrypt("Hello World!")
    plain: str = cryptor.decrypt(cipher)
    assert plain == "Hello World!"
    with pytest.raises(DecryptionError):
        tempered: list[str] = list(cipher)
        random.shuffle(tempered)
        tempered_cipher: str = "".join(tempered)
        plain = cryptor.decrypt(tempered_cipher)


def test_gcm() -> None:
    cryptor: ICryptor = Gcm(key=Key(size=32))
    cipher: str = cryptor.encrypt("Hello World!")
    plain: str = cryptor.decrypt(cipher)
    assert plain == "Hello World!"
    with pytest.raises(DecryptionError):
        tempered: list[str] = list(cipher)
        random.shuffle(tempered)
        tempered_cipher: str = "".join(tempered)
        plain = cryptor.decrypt(tempered_cipher)
