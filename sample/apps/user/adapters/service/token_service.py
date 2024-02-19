from sample.apps.user.domain.interface.service.token_service import IAsyncTokenService
from sample.apps.user.domain.model.user import User
from sample.common.config import ServerConfiguration, TokenSetting
from spakky.cryptography.jwt import JWT
from spakky.dependency.autowired import autowired
from spakky.dependency.component import Component


@Component()
class AsyncTokenService(IAsyncTokenService):
    __token_setting: TokenSetting

    @autowired
    def __init__(self, config: ServerConfiguration) -> None:
        self.__token_setting = config.token_setting

    async def generate_token(self, user: User) -> str:
        return (
            JWT()
            .set_hash_type(self.__token_setting.algorithm)
            .set_expiration(self.__token_setting.expire_after)
            .set_payload(sub=str(user.uid))
            .sign(self.__token_setting.secret_key)
            .export()
        )
