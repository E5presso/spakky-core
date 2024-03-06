import random

import pytest

from spakky.cryptography.cryptor.interface import ICryptor
from spakky.cryptography.cryptor.rsa import AsymmetricKey, Rsa
from spakky.cryptography.error import (
    DecryptionFailedError,
    InvalidAsymmetricKeyFormatError,
    KeySizeError,
)


@pytest.mark.parametrize("size", [1024, 2048])
def test_rsa_with_generated_key(size: int) -> None:
    cryptor: ICryptor = Rsa(key=AsymmetricKey(size=size))
    cipher: str = cryptor.encrypt("Hello World!")
    plain: str = cryptor.decrypt(cipher)
    assert plain == "Hello World!"
    with pytest.raises(DecryptionFailedError):
        tempered: str = "".join(random.sample(cipher, len(cipher)))
        plain = cryptor.decrypt(tempered)


@pytest.mark.parametrize(
    "key",
    [
        b"""-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCIrnR6JZEw1xPkI8K1VWuJq45opto6DW5hHjDvfZ/Y+BLFO8xw
JyxjqgGZ7hVZw8gHAUpArjPzZb5ICNfSz6kAeVYMZdH0SEMr5NRFUY6m32d5MezI
DfktS3OeraalGl3ECJ+XRU1t1peSS7aleutEKl3W0SWs7TfeKnfdaVoaJQIDAQAB
AoGAXjLVhaVEdkOUquPWekDft2br48YymlXNX9N96GBM/SyjSxlWYWkuF5YAOoUy
Y8YhompKMV+d4D6bsGufyuNhVjCU7zWUc82NZ9ZtspBJaCL0T2HcWU2TbD5HTIAs
VLRCQWatqIvdiSl316VB22mO95aHY6rZbfR2Ivju6uOaxxUCQQDrgIP+mbkK3LGj
ovTJ7QaV6EdueWKswdNOotQIr81YaWisAupLj7D60t7Yx39CIhUzrMguAX92LWww
VYyHyoKTAkEAlJQCCE7DvpNAW8Qj8N3YPPT/tDp6fjEcuyf1cgLb/mzSyh1Ylu1k
lORN5b68giAyDjO3lVV416kDKKaX5XfLZwJBAJ4CiI2XDrTfBsFIYP3q7vQ9+U+C
WlaXZfPpBGMfsaOUdgqTmihArPpd6e+BSz1QKPGXCGj10FO2flSf0b56fckCQHmR
bORNRh5Nr7AmGV5AtmiR8hMOciGEn8SG2m5R5p0Tf5l+T3kWfmDROOeNnAJAw5QZ
PtICYGDc2kfNn6VS0msCQGqtovYBRrVgTtOgVD+vOyq9su6AauXpQzuGJEvfC+Mn
fMqQ9TP1ljw78GCUSiqoh+1kfCeHa7jGTOmgcy6u2dQ=
-----END RSA PRIVATE KEY-----""",
        b"""-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQBjLpQXruvhhOO/w3p6tYm1Zs4hX4elsre9r443wt1HObclIpZO
6mSvXccmNAUwJf/QCYLlutMzhD91pugWC2IoVDt62RPzGvdWi39f1lVhPTiwLnyX
vse/2yng68BJDvBO8RzKYE07kaPuiNtiSWwFMlnVsk/y3PBlnvapy1/YsioJpkLV
bZwcEO6CmAWIKEAajWZ3UAaKA1CNYby8/lmyZh4FduHwsZLYkmCMa5bgGeNPJs+T
oiKRkvKTuZnfv9y0Y5v5M3km6PVUd6EPCJypPXO1MVv5lNOgT55asJMq2F/HnPmv
LVxDMtyRroglo72foSrHxKGX5i+KFXgUVA5JAgMBAAECggEACWfWZXSSK/3VN09L
Yy2qFIjeTW3oyD7ti9CFNSaGo4WGp7/i7zLtP3AuPaI7R7iizNDKGA0ikEUfW4Hr
ioOj2F08ksbZTHmnMQ7jkmwaBrGumY6fBCj0em5HR2wz/Pmssl/NMif1ywtht3JF
E8oQs2F2AXz6dfab2Zc8nxeJTFxivLbZS4HAH6B2NM9ghsLjV/wSdZyU307qaZ7d
QWArn8A4MWJpJVi0aTSicJH8ZoNYqE0E+TB/6yPzDwuKSVhCAJAdpsgiVpVT0LF6
DphrWSfl34X3rnzPFY6OwtfGnOKWwXsdQtbeQ2zhkAnizjgfTbatMOjbd2ATU6vR
BqqjnQKBgQCnBBFPZD6xN/6wpcCxNd0ufA/hFgNMZPRWK7eg9fR3TDeC0zjrNtL1
X04U5dWxcqJ/SKC9HOl0Ywn7cOd+gk8KPqDvEMF5z5RBmaCXQBZjeIakZlkzTunf
Str+6CwELGMv3bH6iUqwcLwTDdFsOQ6otM7WR/x9cxZGiBWWIMu4QwKBgQCYBmGr
DjNB/l40QQi0AG4osO02OYICBuppiHRmpvmIHMlnMFKJiiLBJgTAv1LWyMvoLf9o
lbfvPJYjYAFhT740gEznCEDaHc0gjgM0epv480nmhaz7i00uULEzguO7Pyj1QV8A
Dlw4eeXrirlcq+p9V6XuMtXssQtHOKdVzP3sgwKBgQCPR6cOBALgiBggNWKU5I/G
lDoPMJJN1IHk9wZGuRoryiAJROmcqGDcjhFvTilAXQbYyVbURlxlM53Zrud6GZJz
SH1J+obw2Ero6EHj3+AVH83qdb9qi/WJUS+E5Wr1fZrt8nQAag3ARkai1gTmoiBY
TRzwqbsLaFMg2Rgjvijm/wKBgGUNYOCeSM4mMiJT1GAqJQ9hQ9yWb2e/hxPtQ0p0
1Ut3rxyrT0Hjk2SGTAR/aKYixP+pi6vOUXxx7m7HQ0OXCRzG59ducgVKZ+6q11CL
65+YwFe+JZTzLLOLqa5O4+e0fRpBgM99vClCReXCyaHjGLSGjWJ/Yhm6OX/3Fav/
3g3XAoGAB6D8Yp4TujvD6TaPAgzanqA/GigjBUVzpAMhG+iPaNUVcyECVUHrsjSQ
7chGeiaQu/9CFsAnZ7XCqAF000AJllkr/MvvmjJifJwK0ORmXqYXPG4o53W7qnw+
qv61owZbeHyuRVzfHwu6nqD2TXUJGfG8H9rsj1KgIoaJI1tpmkg=
-----END RSA PRIVATE KEY-----""",
    ],
)
def test_rsa_with_existing_key(key: bytes) -> None:
    cryptor: ICryptor = Rsa(key=AsymmetricKey(key=key))
    cipher: str = cryptor.encrypt("Hello World!")
    plain: str = cryptor.decrypt(cipher)
    assert plain == "Hello World!"
    with pytest.raises(DecryptionFailedError):
        tempered: str = "".join(random.sample(cipher, len(cipher)))
        plain = cryptor.decrypt(tempered)


def test_asymmetric_key_expect_key_size_error() -> None:
    with pytest.raises(KeySizeError, match="512"):
        Rsa(key=AsymmetricKey(size=512))
    with pytest.raises(KeySizeError, match="512"):
        Rsa(
            key=AsymmetricKey(
                key=b"""-----BEGIN RSA PRIVATE KEY-----
MIIBOgIBAAJBAM/sRQOF/0MbVrq8nYdgf92X/E2JtfbyGvAky1nwexL1VuriiaE0
vopCKP1O+qiIugfl3gTbmtIle3sIqKixA9cCAwEAAQJBAMx4nFHft2yF+R+AlyXn
hzci3NJfp9umsUkR1gynilDTv5Bg+Qud2NH39PRNQmuulHQJdXCYyOMo7+Gs40FU
GjECIQD2tag7B6bIGJ1qVhE5IygexlC5DZkBQnB70XZgbI9H6QIhANfAsvqPHsPa
AhwrDj0I4wHQb83wr3VMyw1CsrP3WlW/AiBm9QyOBfVuUAdxlxV8+NUHcs/BSpFt
2yJCKfny55sr8QIgTFR+faq4xa2RZYnOBcXpGjE1/PQT/znl9JEOTCFMsl0CIDyF
JL53zbfJ0YSeewnfXuy2kBZb7nF27V/GX1FQjS7D
-----END RSA PRIVATE KEY-----"""
            )
        )


def test_asymmetric_key_expect_invalid_key_error() -> None:
    with pytest.raises(InvalidAsymmetricKeyFormatError):
        Rsa(key=AsymmetricKey(key=b"invalid key format"))
