from datetime import timedelta

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from spakky.cryptography.hmac import HMACType
from spakky.cryptography.key import Key
from spakky.stereotypes.configuration import Configuration


class TokenSetting(BaseModel):
    secret_key_string: str
    url_safe: bool
    expire_after_hours: int
    algorithm: HMACType

    @property
    def expire_after(self) -> timedelta:
        return timedelta(hours=self.expire_after_hours)

    @property
    def secret_key(self) -> Key:
        return Key(base64=self.secret_key_string, url_safe=self.url_safe)


@Configuration()
class ServerConfiguration(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="sample/.env", env_file_encoding="utf-8", env_nested_delimiter="__"
    )
    debug: bool
    token_setting: TokenSetting
