from __future__ import annotations
import json
from uuid import UUID, uuid4
from typing import Any, final, overload
from datetime import datetime, timedelta
from spakky.cryptography.key import Key
from spakky.cryptography.b64 import Base64Encoder
from spakky.cryptography.hash import Hash, HashType
from spakky.cryptography.hmac import HMAC


@final
class InvalidTokenError(BaseException):
    def __str__(self) -> str:
        return "parameter 'token' is not a valid data (which has 3 separated values.)"


@final
class TokenDecodingError(BaseException):
    def __str__(self) -> str:
        return "parameter 'token' is not a valid data (json decoding error.)"


@final
class JWT:
    __header: dict[str, Any]
    __payload: dict[str, Any]
    __sign_key: Key | None
    __signature: str | None
    __signed: bool = False

    @property
    def id(self) -> UUID:
        key: str | None = self.__payload.get("jti")
        if key is None:
            raise Exception("field named 'jti' does not exists in payload")
        return UUID(key)

    @property
    def round(self) -> int:
        round: int | None = self.__payload.get("rnd")
        if round is None:
            raise Exception("field named 'rnd' does not exists in payload")
        return round

    @property
    def payload(self) -> dict[str, Any]:
        return self.__payload

    @property
    def updated_at(self) -> datetime:
        updated_at: int | None = self.__payload.get("updated_at")
        if updated_at is None:
            raise Exception("field named 'updated_at' does not exists in payload")
        return self.__convert_datetime(updated_at)

    @property
    def hash(self) -> str:
        hash: str | None = self.__payload.get("c_hash")
        if hash is None:
            raise Exception("field named 'c_hash' does not exists in payload")
        return hash

    @property
    def last_authorized(self) -> datetime:
        last_authorized: int | None = self.__payload.get("auth_time")
        if last_authorized is None:
            raise Exception("field named 'auth_time' does not exists in payload")
        return self.__convert_datetime(last_authorized)

    @property
    def expired(self) -> bool:
        exp_value: int | None = self.__payload.get("exp")
        if exp_value is None:
            raise Exception("exp field cannot be None in payload")
        expiration_date: datetime = self.__convert_datetime(exp_value)
        return expiration_date < datetime.now()

    @overload
    def __init__(self) -> None:
        ...

    @overload
    def __init__(self, token: str) -> None:
        ...

    def __init__(self, token: str | None = None) -> None:
        if token is not None:
            parts: list[str] = token.split(".")
            if len(parts) != 3:
                raise InvalidTokenError
            [header, body, signature] = parts
            try:
                self.__header = json.loads(Base64Encoder.decode(b64=header, url_safe=True))
                self.__payload = json.loads(Base64Encoder.decode(b64=body, url_safe=True))
            except:
                raise TokenDecodingError
            self.__signature = signature
            self.__signed = False
        else:
            id: UUID = uuid4()
            current_time: datetime = datetime.now()
            self.__header = {
                "typ": "JWT",
                "alg": HashType.HS256,
            }
            self.__payload = {
                "jti": str(id),
                "iat": self.__convert_unixtime(current_time),
                "updated_at": self.__convert_unixtime(current_time),
                "auth_time": self.__convert_unixtime(current_time),
                "c_hash": Hash(data=str(id), hash_type=HashType.SHA1).hex,
                "rnd": 0,
            }

    def __sign(self) -> None:
        header: str = Base64Encoder.encode(utf8=json.dumps(self.__header), url_safe=True)
        payload: str = Base64Encoder.encode(utf8=json.dumps(self.__payload), url_safe=True)
        data_to_sign: str = f"{header}.{payload}"
        sign_algorithm: HashType | None = self.__header.get("alg")
        if self.__sign_key is None:
            raise Exception("sign key cannot be None")
        if sign_algorithm is None:
            raise Exception("field named 'alg' does not exists in header")
        self.__signature = HMAC.sign_text(
            self.__sign_key,
            sign_algorithm,
            data_to_sign,
            True,
        )
        self.__signed = True

    def __convert_datetime(self, unix_time: int) -> datetime:
        return datetime.fromtimestamp(float(unix_time))

    def __convert_unixtime(self, date_time: datetime) -> int:
        return int(date_time.timestamp())

    def set_header(self, **kwargs) -> JWT:
        for key, value in kwargs.items():
            self.__header[key] = value
        if self.__signed:
            self.__sign()
        return self

    def set_payload(self, **kwargs) -> JWT:
        for key, value in kwargs.items():
            self.__payload[key] = value
        if self.__signed:
            self.__sign()
        return self

    def set_hash_type(self, hash_type: HashType) -> JWT:
        if hash_type not in [HashType.HS256, HashType.HS384, HashType.HS512]:
            raise Exception("hash_type must be one of type (HS256 | HS384 | HS512)")
        self.__header["alg"] = hash_type
        if self.__signed:
            self.__sign()
        return self

    def set_expiration(self, expire_after: timedelta) -> JWT:
        iat_value: int | None = self.__payload.get("iat")
        if iat_value is None:
            raise Exception("field named 'iat' does not exists in payload")
        iat: datetime = self.__convert_datetime(iat_value)
        exp: int = self.__convert_unixtime(iat + expire_after)
        self.__payload["exp"] = exp
        self.__payload["updated_at"] = self.__convert_unixtime(datetime.now())
        if self.__signed:
            self.__sign()
        return self

    def refresh(self, expire_after: timedelta) -> JWT:
        rnd_value: int | None = self.__payload.get("rnd")
        hash_value: str | None = self.__payload.get("c_hash")
        if rnd_value is None:
            raise Exception("field named 'rnd' does not exists in payload")
        if hash_value is None:
            raise Exception("field named 'c_hash' does not exists in payload")
        current_time: datetime = datetime.now()
        self.__payload["exp"] = self.__convert_unixtime(current_time + expire_after)
        self.__payload["updated_at"] = self.__convert_unixtime(current_time)
        self.__payload["c_hash"] = Hash(data=hash_value, hash_type=HashType.SHA1).hex
        self.__payload["rnd"] = rnd_value + 1
        if self.__signed:
            self.__sign()
        return self

    def sign(self, key: Key) -> JWT:
        self.__sign_key = key
        self.__sign()
        return self

    def verify(self, key: Key) -> bool:
        self.__sign_key = key
        header: str = Base64Encoder.encode(utf8=json.dumps(self.__header), url_safe=True)
        payload: str = Base64Encoder.encode(utf8=json.dumps(self.__payload), url_safe=True)
        content: str = f"{header}.{payload}"
        sign_algorithm: HashType | None = self.__header.get("alg")
        if self.__sign_key is None:
            raise Exception("sign key cannot be None")
        if self.__signature is None:
            raise Exception("signature cannot be None")
        if sign_algorithm is None:
            raise Exception("field named 'alg' does not exists in header")
        verification_result: bool = HMAC.verify(
            key=self.__sign_key,
            hash_type=sign_algorithm,
            content=content,
            signature=self.__signature,
            url_safe=True,
        )
        if verification_result:
            self.__payload["auth_time"] = self.__convert_unixtime(datetime.now())
            self.__signed = verification_result
        return verification_result

    def export(self) -> str:
        if self.__signed:
            header: str = Base64Encoder.encode(utf8=json.dumps(self.__header), url_safe=True)
            payload: str = Base64Encoder.encode(json.dumps(self.__payload), url_safe=True)
            return f"{header}.{payload}.{self.__signature}"
        else:
            raise Exception("Token must be signed")
