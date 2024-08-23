from spakky.security.encoding import Base64Encoder

MESSAGE: str = "Hello World! I'm Program!"


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
        binary=bytes(
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
        binary=bytes(
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
