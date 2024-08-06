from spakky.application.interfaces.pluggable import IPluggable
from spakky.application.interfaces.registry import IRegistry
from spakky.extensions.transactional import (
    AsyncTransactionalAdvisor,
    TransactionalAdvisor,
)


class TransactionPlugin(IPluggable):
    def register(self, registry: IRegistry) -> None:
        registry.register_bean(TransactionalAdvisor)
        registry.register_bean(AsyncTransactionalAdvisor)
